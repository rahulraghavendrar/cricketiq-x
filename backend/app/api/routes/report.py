"""
CricketIQ X - Report generation endpoints
Serves all 5 pages of the match intelligence report.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.models import Player, Match, BallEvent, PitchProfile
from app.gemini.match_summary import generate_match_summary, generate_toss_advice
from app.gemini.player_advice import generate_batsman_advice, generate_bowler_advice
from app.gemini.match_plan    import generate_batting_plan, generate_bowling_plan
from app.scrapers.pitch_report import get_pitch_report, get_weather
from typing import Optional
import pandas as pd
from pathlib import Path

router = APIRouter(prefix="/api/report", tags=["report"])

PROCESSED_DIR = Path(__file__).parent.parent.parent.parent.parent / "data" / "processed"


def _load_features(player_id: int, feature_type: str) -> dict:
    """Load batting or bowling features for a player."""
    path = PROCESSED_DIR / f"{feature_type}_features.csv"
    if not path.exists():
        return {}
    df  = pd.read_csv(path)
    row = df[df['player_id'] == player_id]
    return row.iloc[0].to_dict() if not row.empty else {}


# ── Page 1: Match Summary ────────────────────────────────────
@router.get("/page1/{team1}/{team2}")
def page1_match_summary(
    team1:     str,
    team2:     str,
    venue:     str = Query("MA Chidambaram Stadium, Chepauk, Chennai"),
    db:        Session = Depends(get_db)
):
    # Pitch report
    pitch = get_pitch_report(venue)

    # Weather
    weather = get_weather(venue)

    # Historical venue stats
    venue_profile = db.query(PitchProfile).filter(
        PitchProfile.venue_name.ilike(f"%{venue.split(',')[0].strip()}%")
    ).first()

    avg_first_innings = float(venue_profile.avg_first_innings) if venue_profile else 170.0

    # Head to head
    csk_name = "Chennai Super Kings"
    h2h_matches = db.query(Match).filter(
        ((Match.team1 == csk_name) | (Match.team2 == csk_name)) &
        ((Match.team1 == team2)    | (Match.team2 == team2))
    ).all()

    csk_wins  = sum(1 for m in h2h_matches if m.winner == csk_name)
    total_h2h = len(h2h_matches)
    csk_win_pct = round(csk_wins / total_h2h * 100, 1) if total_h2h > 0 else 50.0

    # Win probability (simple model based on form + h2h)
    win_prob_csk = min(75, max(25, csk_win_pct + 5))

    # Predicted score
    pitch_type     = pitch.get('pitch_type', 'flat')
    score_modifier = {'turner': -10, 'green_seamer': -5, 'flat': +10, 'variable': 0}
    predicted_score = int(avg_first_innings + score_modifier.get(pitch_type, 0))

    # Gemini summary
    gemini_summary = generate_match_summary(
        team1           = "CSK",
        team2           = team2,
        venue           = venue,
        pitch_type      = pitch_type,
        spin_index      = pitch.get('spin_assistance', 0.35),
        pace_index      = pitch.get('pace_assistance', 0.50),
        dew_factor      = weather.get('dew_factor', 'medium'),
        avg_first_innings = avg_first_innings,
        csk_win_pct     = csk_win_pct,
        key_matchups    = [],
    )

    toss_advice = generate_toss_advice(
        venue           = venue,
        pitch_type      = pitch_type,
        dew_factor      = weather.get('dew_factor', 'medium'),
        avg_first_innings = avg_first_innings,
        csk_form        = 6.5,
        opponent_form   = 6.0,
    )

    return {
        "match": {
            "team1":    "CSK",
            "team2":    team2,
            "venue":    venue,
        },
        "pitch": pitch,
        "weather": weather,
        "predictions": {
            "win_probability_csk":      win_prob_csk,
            "win_probability_opponent": 100 - win_prob_csk,
            "predicted_avg_score":      predicted_score,
            "predicted_winning_score":  predicted_score + 5,
            "dew_factor":               weather.get('dew_factor', 'medium'),
            "toss_advantage_score":     0.65 if weather.get('dew_factor') == 'high' else 0.45,
        },
        "head_to_head": {
            "total":        total_h2h,
            "csk_wins":     csk_wins,
            "opp_wins":     total_h2h - csk_wins,
            "csk_win_pct":  csk_win_pct,
        },
        "venue_stats": {
            "avg_first_innings":  avg_first_innings,
            "sample_matches":     venue_profile.sample_matches if venue_profile else 0,
            "spin_wicket_pct":    venue_profile.spin_wicket_pct if venue_profile else 35.0,
            "pace_wicket_pct":    venue_profile.pace_wicket_pct if venue_profile else 65.0,
        },
        "gemini": {
            "match_summary": gemini_summary,
            "toss_advice":   toss_advice,
        },
    }


# ── Page 2: Player Profiles ──────────────────────────────────
@router.get("/page2/player/{player_id}")
def page2_player_profile(
    player_id:  str,
    opponent:   str = Query("RCB"),
    pitch_type: str = Query("flat"),
    venue:      str = Query("M Chinnaswamy Stadium"),
    db:         Session = Depends(get_db)
):
    from app.ml.weakness_detector import predict_weakness

    player = db.query(Player).filter(Player.player_id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    is_csk    = player.ipl_team == 'CSK'
    bat_feats = _load_features(player.id, 'batting')
    bowl_feats= _load_features(player.id, 'bowling')

    # ML weakness prediction
    weakness = {}
    if bat_feats:
        weakness = predict_weakness(bat_feats)

    # Opponent players for context
    opp_players = db.query(Player).filter(
        Player.ipl_team == opponent
    ).all()

    opp_bowlers  = [p.name for p in opp_players if p.role in ['bowler','allrounder']][:5]
    opp_batters  = [p.name for p in opp_players if p.role in ['batter','allrounder','wicketkeeper']][:5]

    # Gemini advice
    gemini_advice = ""
    if player.role in ['batter', 'allrounder', 'wicketkeeper'] and bat_feats:
        gemini_advice = generate_batsman_advice(
            player_name       = player.name,
            team              = player.ipl_team or 'Unknown',
            is_csk_player     = is_csk,
            stats             = bat_feats,
            weakness_label    = weakness.get('weakness_label', 'balanced'),
            confidence        = weakness.get('confidence_pct', 50),
            opponent_bowlers  = opp_bowlers if is_csk else opp_batters,
            pitch_type        = pitch_type,
            venue             = venue,
        )
    elif player.role in ['bowler', 'allrounder'] and bowl_feats:
        gemini_advice = generate_bowler_advice(
            player_name           = player.name,
            team                  = player.ipl_team or 'Unknown',
            is_csk_player         = is_csk,
            stats                 = bowl_feats,
            pitch_type            = pitch_type,
            venue                 = venue,
            key_opposition_batters= opp_batters if is_csk else opp_bowlers,
        )

    return {
        "player": {
            "player_id":     player.player_id,
            "name":          player.name,
            "role":          player.role,
            "bowling_style": player.bowling_style,
            "ipl_team":      player.ipl_team,
            "is_csk":        is_csk,
        },
        "batting_stats":  bat_feats if bat_feats else None,
        "bowling_stats":  bowl_feats if bowl_feats else None,
        "weakness":       weakness if weakness else None,
        "gemini_advice":  gemini_advice,
    }


# ── Page 2: Full team squad ──────────────────────────────────
@router.get("/page2/squad/{team}")
def page2_squad(team: str, db: Session = Depends(get_db)):
    players = db.query(Player).filter(Player.ipl_team == team).all()
    if not players:
        raise HTTPException(status_code=404, detail=f"Team not found: {team}")

    result = []
    for p in players:
        bat_feats  = _load_features(p.id, 'batting')
        bowl_feats = _load_features(p.id, 'bowling')
        result.append({
            "player_id":     p.player_id,
            "name":          p.name,
            "role":          p.role,
            "bowling_style": p.bowling_style,
            "batting": {
                "strike_rate":  bat_feats.get('strike_rate', 0),
                "average":      bat_feats.get('average', 0),
                "powerplay_sr": bat_feats.get('powerplay_sr', 0),
                "death_sr":     bat_feats.get('death_sr', 0),
                "vs_spin_sr":   bat_feats.get('vs_spin_sr', 0),
                "vs_pace_sr":   bat_feats.get('vs_pace_sr', 0),
            } if bat_feats else None,
            "bowling": {
                "economy":       bowl_feats.get('economy', 0),
                "wicket_rate":   bowl_feats.get('wicket_rate', 0),
                "death_economy": bowl_feats.get('death_economy', 0),
                "dot_ball_pct":  bowl_feats.get('dot_ball_pct', 0),
                "pp_economy":    bowl_feats.get('pp_economy', 0),
            } if bowl_feats else None,
        })

    return {"team": team, "players": result, "count": len(result)}


# ── Page 4: Match Plan ───────────────────────────────────────
@router.get("/page4/{opponent}")
def page4_match_plan(
    opponent:   str,
    venue:      str = Query("MA Chidambaram Stadium, Chepauk, Chennai"),
    pitch_type: str = Query("flat"),
    db:         Session = Depends(get_db)
):
    # Get CSK squad
    csk_players  = db.query(Player).filter(Player.ipl_team == 'CSK').all()
    opp_players  = db.query(Player).filter(Player.ipl_team == opponent).all()

    csk_batters  = [p.name for p in csk_players if p.role in ['batter','allrounder','wicketkeeper']]
    csk_bowlers  = [p.name for p in csk_players if p.role in ['bowler','allrounder']]
    opp_batters  = [p.name for p in opp_players if p.role in ['batter','allrounder','wicketkeeper']]
    opp_bowlers  = [p.name for p in opp_players if p.role in ['bowler','allrounder']]

    # Build bowling rotation based on pitch type
    spin_bowlers = [p.name for p in csk_players
                    if p.role in ['bowler','allrounder']
                    and p.bowling_style and 'spin' in p.bowling_style]
    pace_bowlers = [p.name for p in csk_players
                    if p.role in ['bowler','allrounder']
                    and p.bowling_style and 'pace' in p.bowling_style]

    # Phase targets based on pitch
    phase_targets = {
        'turner':       {'powerplay': '40-50', 'middle': '65-75', 'death': '50-60'},
        'green_seamer': {'powerplay': '45-55', 'middle': '65-75', 'death': '50-60'},
        'flat':         {'powerplay': '50-60', 'middle': '70-85', 'death': '60-70'},
        'variable':     {'powerplay': '42-52', 'middle': '65-75', 'death': '52-62'},
    }
    targets = phase_targets.get(pitch_type, phase_targets['flat'])

    score_map  = {'turner': 155, 'green_seamer': 160, 'flat': 178, 'variable': 162}
    target_score    = score_map.get(pitch_type, 170)
    defensive_score = score_map.get(pitch_type, 170) - 5

    # Gemini plans
    batting_plan = generate_batting_plan(
        venue              = venue,
        pitch_type         = pitch_type,
        dew_factor         = 'medium',
        batting_order      = csk_batters[:6],
        phase_targets      = targets,
        bowlers_to_attack  = opp_bowlers[-3:],
        bowlers_to_respect = opp_bowlers[:2],
        target_score       = target_score,
    )

    bowling_plan = generate_bowling_plan(
        venue             = venue,
        pitch_type        = pitch_type,
        dew_factor        = 'medium',
        bowling_rotation  = csk_bowlers[:6],
        key_matchups      = [f"{b} vs {bat}" for b in csk_bowlers[:3] for bat in opp_batters[:2]][:6],
        defensive_target  = defensive_score,
    )

    return {
        "opponent":         opponent,
        "venue":            venue,
        "pitch_type":       pitch_type,
        "batting_plan": {
            "batting_order":       csk_batters[:7],
            "phase_targets":       targets,
            "target_score":        target_score,
            "bowlers_to_attack":   opp_bowlers[-3:],
            "bowlers_to_respect":  opp_bowlers[:2],
            "spin_bowlers":        spin_bowlers,
            "pace_bowlers":        pace_bowlers,
            "gemini_narrative":    batting_plan,
        },
        "bowling_plan": {
            "bowling_rotation":    csk_bowlers[:8],
            "spin_bowlers":        spin_bowlers,
            "pace_bowlers":        pace_bowlers,
            "defensive_target":    defensive_score,
            "key_opp_batters":     opp_batters[:6],
            "gemini_narrative":    bowling_plan,
        },
    }


# ── Upcoming match ───────────────────────────────────────────
@router.get("/upcoming")
def upcoming_match():
    from app.scrapers.live_score import get_upcoming_csk_match
    return get_upcoming_csk_match()


# ── Live score ───────────────────────────────────────────────
@router.get("/live-score")
def live_score():
    from app.scrapers.live_score import get_live_csk_score
    return get_live_csk_score()
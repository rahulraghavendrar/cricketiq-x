from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.models import Player, BallEvent, Match, Partnership
from typing import Optional
import pandas as pd
from pathlib import Path

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

PROCESSED_DIR = Path(__file__).parent.parent.parent.parent.parent / "data" / "processed"


# ── 1. Raw head-to-head matchup stats ───────────────────────
@router.get("/matchup")
def matchup_stats(
    batter_id: str,
    bowler_id: str,
    db: Session = Depends(get_db)
):
    batter = db.query(Player).filter(Player.player_id == batter_id).first()
    bowler = db.query(Player).filter(Player.player_id == bowler_id).first()

    if not batter or not bowler:
        raise HTTPException(status_code=404, detail="Player not found")

    events = (
        db.query(BallEvent)
        .filter(BallEvent.batter_id == batter.id)
        .filter(BallEvent.bowler_id == bowler.id)
        .all()
    )

    if not events:
        return {"message": "No head-to-head data found", "balls": 0}

    total_balls   = len(events)
    total_runs    = sum(e.runs_batter for e in events)
    total_wickets = sum(1 for e in events if e.is_wicket)
    dot_balls     = sum(1 for e in events if e.runs_batter == 0 and not e.is_wicket)
    boundaries    = sum(1 for e in events if e.runs_batter >= 4)
    sr            = round(total_runs / total_balls * 100, 1) if total_balls > 0 else 0

    dismissal_types = {}
    for e in events:
        if e.is_wicket and e.dismissal_type:
            dismissal_types[e.dismissal_type] = dismissal_types.get(e.dismissal_type, 0) + 1

    return {
        "batter":          batter.name,
        "bowler":          bowler.name,
        "balls":           total_balls,
        "runs":            total_runs,
        "wickets":         total_wickets,
        "strike_rate":     sr,
        "dot_balls":       dot_balls,
        "dot_ball_pct":    round(dot_balls / total_balls * 100, 1) if total_balls > 0 else 0,
        "boundaries":      boundaries,
        "dismissal_types": dismissal_types,
        "advantage":       "bowler" if total_wickets > 1 or sr < 100 else "batter",
    }


# ── 2. Rule-based weakness from raw ball events ──────────────
@router.get("/weakness/{player_id}")
def player_weakness(
    player_id: str,
    venue: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    player = db.query(Player).filter(Player.player_id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    q = db.query(BallEvent).filter(BallEvent.batter_id == player.id)
    if venue:
        match_ids = [m.id for m in db.query(Match).filter(Match.venue == venue).all()]
        q = q.filter(BallEvent.match_id.in_(match_ids))

    events = q.all()
    if not events:
        return {"player": player.name, "weakness": "insufficient data"}

    dismissals = {}
    for e in events:
        if e.is_wicket and e.dismissal_type:
            dismissals[e.dismissal_type] = dismissals.get(e.dismissal_type, 0) + 1

    def phase_stats(evts):
        if not evts:
            return {"sr": 0, "wickets": 0, "balls": 0}
        runs  = sum(e.runs_batter for e in evts)
        wkts  = sum(1 for e in evts if e.is_wicket)
        balls = len(evts)
        return {"sr": round(runs / balls * 100, 1), "wickets": wkts, "balls": balls}

    primary_weakness = max(dismissals, key=dismissals.get) if dismissals else "unknown"
    total_dismissals = sum(dismissals.values())

    return {
        "player":              player.name,
        "primary_weakness":    primary_weakness,
        "confidence_pct":      round(dismissals.get(primary_weakness, 0) / total_dismissals * 100, 1) if total_dismissals > 0 else 0,
        "dismissal_breakdown": dismissals,
        "phase_stats": {
            "powerplay": phase_stats([e for e in events if e.over < 6]),
            "middle":    phase_stats([e for e in events if 6 <= e.over < 15]),
            "death":     phase_stats([e for e in events if e.over >= 15]),
        },
        "total_balls": len(events),
    }


# ── 3. CSK vs opponent head-to-head ─────────────────────────
@router.get("/csk/head-to-head/{opponent}")
def csk_vs_opponent(opponent: str, db: Session = Depends(get_db)):
    csk_matches = (
        db.query(Match)
        .filter(
            ((Match.team1 == "Chennai Super Kings") | (Match.team2 == "Chennai Super Kings")) &
            ((Match.team1 == opponent) | (Match.team2 == opponent))
        )
        .all()
    )

    if not csk_matches:
        return {"message": f"No matches found between CSK and {opponent}"}

    csk_wins  = sum(1 for m in csk_matches if m.winner == "Chennai Super Kings")
    opp_wins  = sum(1 for m in csk_matches if m.winner == opponent)
    no_result = len(csk_matches) - csk_wins - opp_wins

    return {
        "csk":         "Chennai Super Kings",
        "opponent":    opponent,
        "total":       len(csk_matches),
        "csk_wins":    csk_wins,
        "opp_wins":    opp_wins,
        "no_result":   no_result,
        "csk_win_pct": round(csk_wins / len(csk_matches) * 100, 1),
        "seasons":     sorted(list(set(m.season for m in csk_matches))),
    }


# ── 4. ML weakness prediction (XGBoost) ─────────────────────
@router.get("/ml/weakness/{player_id}")
def ml_weakness(player_id: str, db: Session = Depends(get_db)):
    from app.ml.weakness_detector import predict_weakness

    player = db.query(Player).filter(Player.player_id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail=f"Player not found: {player_id}")

    bat_path = PROCESSED_DIR / "batting_features.csv"
    if not bat_path.exists():
        raise HTTPException(status_code=500, detail="Features not computed. Run train_models.py first.")

    df  = pd.read_csv(bat_path)
    row = df[df['player_id'] == player.id]

    if row.empty:
        return {
            "player":    player.name,
            "player_id": player_id,
            "role":      player.role,
            "message":   "No batting feature data — player may be a pure bowler or had fewer than 30 balls faced",
        }

    features = row.iloc[0].to_dict()
    result   = predict_weakness(features)
    result['player']         = player.name
    result['player_id']      = player_id
    result['role']           = player.role
    result['bowling_style']  = player.bowling_style
    return result


# ── 5. ML matchup prediction (LightGBM) ─────────────────────
@router.get("/ml/matchup-predict")
def ml_matchup_predict(
    batter_id: str,
    bowler_id: str,
    phase: str = "middle",
    db: Session = Depends(get_db)
):
    from app.ml.matchup_predictor import predict_matchup

    batter = db.query(Player).filter(Player.player_id == batter_id).first()
    bowler = db.query(Player).filter(Player.player_id == bowler_id).first()

    if not batter:
        raise HTTPException(status_code=404, detail=f"Batter not found: {batter_id}")
    if not bowler:
        raise HTTPException(status_code=404, detail=f"Bowler not found: {bowler_id}")

    batting_df = pd.read_csv(PROCESSED_DIR / "batting_features.csv")
    bowling_df = pd.read_csv(PROCESSED_DIR / "bowling_features.csv")

    bat_row  = batting_df[batting_df['player_id'] == batter.id]
    bowl_row = bowling_df[bowling_df['player_id'] == bowler.id]

    if bat_row.empty:
        return {"error": f"No batting features for {batter.name}", "batter": batter.name}
    if bowl_row.empty:
        return {"error": f"No bowling features for {bowler.name}", "bowler": bowler.name}

    result = predict_matchup(
        bat_row.iloc[0].to_dict(),
        bowl_row.iloc[0].to_dict(),
        phase
    )
    result['batter'] = batter.name
    result['bowler'] = bowler.name
    result['phase']  = phase
    return result


# ── 6. Full ML feature profile for any player ───────────────
@router.get("/features/{player_id}")
def player_features(player_id: str, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.player_id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail=f"Player not found: {player_id}")

    result = {
        "player":        player.name,
        "player_id":     player_id,
        "role":          player.role,
        "bowling_style": player.bowling_style,
    }

    bat_path = PROCESSED_DIR / "batting_features.csv"
    if bat_path.exists():
        df  = pd.read_csv(bat_path)
        row = df[df['player_id'] == player.id]
        if not row.empty:
            result['batting_features'] = row.iloc[0].to_dict()

    bowl_path = PROCESSED_DIR / "bowling_features.csv"
    if bowl_path.exists():
        df  = pd.read_csv(bowl_path)
        row = df[df['player_id'] == player.id]
        if not row.empty:
            result['bowling_features'] = row.iloc[0].to_dict()

    return result


# ── 7. CSK squad — all players with features ────────────────
@router.get("/csk/squad")
def csk_squad(db: Session = Depends(get_db)):
    csk_names = [
        'MS Dhoni', 'Ruturaj Gaikwad', 'Devon Conway', 'Shivam Dube',
        'Moeen Ali', 'RA Jadeja', 'DL Chahar', 'M Pathirana',
        'SN Thakur', 'MJ Santner', 'TU Deshpande', 'Ajinkya Rahane',
        'MM Ali', 'Washington Sundar', 'Sameer Rizvi',
    ]

    result = []
    batting_df = pd.read_csv(PROCESSED_DIR / "batting_features.csv") if (PROCESSED_DIR / "batting_features.csv").exists() else None
    bowling_df = pd.read_csv(PROCESSED_DIR / "bowling_features.csv") if (PROCESSED_DIR / "bowling_features.csv").exists() else None

    players = db.query(Player).filter(Player.name.in_(csk_names)).all()

    for p in players:
        entry = {
            "player_id":     p.player_id,
            "name":          p.name,
            "role":          p.role,
            "bowling_style": p.bowling_style,
        }
        if batting_df is not None:
            row = batting_df[batting_df['player_id'] == p.id]
            if not row.empty:
                entry['batting'] = {
                    "strike_rate": row.iloc[0]['strike_rate'],
                    "average":     row.iloc[0]['average'],
                    "powerplay_sr":row.iloc[0]['powerplay_sr'],
                    "death_sr":    row.iloc[0]['death_sr'],
                }
        if bowling_df is not None:
            row = bowling_df[bowling_df['player_id'] == p.id]
            if not row.empty:
                entry['bowling'] = {
                    "economy":      row.iloc[0]['economy'],
                    "wicket_rate":  row.iloc[0]['wicket_rate'],
                    "death_economy":row.iloc[0]['death_economy'],
                    "dot_ball_pct": row.iloc[0]['dot_ball_pct'],
                }
        result.append(entry)

    return {"team": "Chennai Super Kings", "players": result}
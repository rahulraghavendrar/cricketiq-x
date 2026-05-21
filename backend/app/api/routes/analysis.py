from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.db.database import get_db
from app.models.models import Player, BallEvent, Match, Partnership
from typing import Optional

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/matchup")
def matchup_stats(
    batter_id: str,
    bowler_id: str,
    db: Session = Depends(get_db)
):
    """Head-to-head stats between a batter and bowler."""
    batter = db.query(Player).filter(Player.player_id == batter_id).first()
    bowler = db.query(Player).filter(Player.player_id == bowler_id).first()

    if not batter or not bowler:
        from fastapi import HTTPException
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

    sr = round(total_runs / total_balls * 100, 1) if total_balls > 0 else 0

    dismissal_types = {}
    for e in events:
        if e.is_wicket and e.dismissal_type:
            dismissal_types[e.dismissal_type] = dismissal_types.get(e.dismissal_type, 0) + 1

    return {
        "batter":         batter.name,
        "bowler":         bowler.name,
        "balls":          total_balls,
        "runs":           total_runs,
        "wickets":        total_wickets,
        "strike_rate":    sr,
        "dot_balls":      dot_balls,
        "dot_ball_pct":   round(dot_balls / total_balls * 100, 1) if total_balls > 0 else 0,
        "boundaries":     boundaries,
        "dismissal_types":dismissal_types,
        "advantage":      "bowler" if total_wickets > 1 or sr < 100 else "batter",
    }


@router.get("/weakness/{player_id}")
def player_weakness(
    player_id: str,
    venue: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Identify primary batting weakness for a player."""
    player = db.query(Player).filter(Player.player_id == player_id).first()
    if not player:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Player not found")

    q = db.query(BallEvent).filter(BallEvent.batter_id == player.id)
    if venue:
        match_ids = [
            m.id for m in db.query(Match).filter(Match.venue == venue).all()
        ]
        q = q.filter(BallEvent.match_id.in_(match_ids))

    events = q.all()
    if not events:
        return {"player": player.name, "weakness": "insufficient data"}

    # Dismissal breakdown
    dismissals = {}
    for e in events:
        if e.is_wicket and e.dismissal_type:
            dismissals[e.dismissal_type] = dismissals.get(e.dismissal_type, 0) + 1

    # Phase vulnerability
    pp_events  = [e for e in events if e.over < 6]
    mid_events = [e for e in events if 6 <= e.over < 15]
    death_events = [e for e in events if e.over >= 15]

    def phase_stats(evts):
        if not evts:
            return {"sr": 0, "wickets": 0, "balls": 0}
        runs = sum(e.runs_batter for e in evts)
        wkts = sum(1 for e in evts if e.is_wicket)
        balls = len(evts)
        return {
            "sr":      round(runs / balls * 100, 1),
            "wickets": wkts,
            "balls":   balls,
        }

    primary_weakness = max(dismissals, key=dismissals.get) if dismissals else "unknown"
    total_dismissals = sum(dismissals.values())

    return {
        "player":           player.name,
        "primary_weakness": primary_weakness,
        "confidence_pct":   round(dismissals.get(primary_weakness, 0) / total_dismissals * 100, 1) if total_dismissals > 0 else 0,
        "dismissal_breakdown": dismissals,
        "phase_stats": {
            "powerplay": phase_stats(pp_events),
            "middle":    phase_stats(mid_events),
            "death":     phase_stats(death_events),
        },
        "total_balls": len(events),
    }


@router.get("/csk/head-to-head/{opponent}")
def csk_vs_opponent(opponent: str, db: Session = Depends(get_db)):
    """CSK win/loss record vs a specific team."""
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
        "csk":        "Chennai Super Kings",
        "opponent":   opponent,
        "total":      len(csk_matches),
        "csk_wins":   csk_wins,
        "opp_wins":   opp_wins,
        "no_result":  no_result,
        "csk_win_pct":round(csk_wins / len(csk_matches) * 100, 1),
        "seasons":    sorted(list(set(m.season for m in csk_matches))),
    }
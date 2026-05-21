from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.db.database import get_db
from app.models.models import Match, BallEvent, PitchProfile
from typing import Optional

router = APIRouter(prefix="/api/matches", tags=["matches"])


@router.get("/")
def list_matches(
    season: Optional[str] = Query(None),
    team: Optional[str]   = Query(None),
    limit: int = 20,
    db: Session = Depends(get_db)
):
    q = db.query(Match).order_by(desc(Match.date))
    if season:
        q = q.filter(Match.season == season)
    if team:
        q = q.filter((Match.team1 == team) | (Match.team2 == team))
    matches = q.limit(limit).all()
    return [
        {
            "id":            m.id,
            "match_id":      m.match_id,
            "date":          str(m.date),
            "season":        m.season,
            "team1":         m.team1,
            "team2":         m.team2,
            "venue":         m.venue,
            "toss_winner":   m.toss_winner,
            "toss_decision": m.toss_decision,
            "winner":        m.winner,
            "result":        m.result,
            "margin":        m.margin,
        }
        for m in matches
    ]


@router.get("/{match_id}/scorecard")
def match_scorecard(match_id: str, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.match_id == match_id).first()
    if not match:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Match not found")

    innings_summary = []
    for inn in [1, 2]:
        events = (
            db.query(BallEvent)
            .filter(BallEvent.match_id == match.id)
            .filter(BallEvent.innings == inn)
            .all()
        )
        if not events:
            continue
        total_runs    = sum(e.runs_total for e in events)
        total_wickets = sum(1 for e in events if e.is_wicket)
        total_balls   = len([e for e in events if e.extras_type not in ["wides", "noballs"]])
        overs         = f"{total_balls // 6}.{total_balls % 6}"
        innings_summary.append({
            "innings":       inn,
            "total_runs":    total_runs,
            "total_wickets": total_wickets,
            "overs":         overs,
        })

    return {
        "match": {
            "id":            match.id,
            "match_id":      match.match_id,
            "date":          str(match.date),
            "venue":         match.venue,
            "team1":         match.team1,
            "team2":         match.team2,
            "winner":        match.winner,
            "toss_winner":   match.toss_winner,
            "toss_decision": match.toss_decision,
        },
        "innings": innings_summary,
    }


@router.get("/seasons/list")
def list_seasons(db: Session = Depends(get_db)):
    seasons = db.query(Match.season).distinct().order_by(desc(Match.season)).all()
    return [s[0] for s in seasons if s[0]]


@router.get("/venues/stats")
def venue_stats(db: Session = Depends(get_db)):
    venues = db.query(PitchProfile).order_by(desc(PitchProfile.sample_matches)).all()
    return [
        {
            "venue_name":       v.venue_name,
            "city":             v.city,
            "spin_wicket_pct":  v.spin_wicket_pct,
            "pace_wicket_pct":  v.pace_wicket_pct,
            "avg_first_innings":v.avg_first_innings,
            "sample_matches":   v.sample_matches,
        }
        for v in venues
    ]
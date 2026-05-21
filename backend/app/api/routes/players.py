from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.db.database import get_db
from app.models.models import Player, BallEvent, Match, CareerStat
from typing import Optional

router = APIRouter(prefix="/api/players", tags=["players"])


@router.get("/")
def list_players(
    team: Optional[str] = Query(None, description="Filter by IPL team"),
    role: Optional[str] = Query(None, description="Filter by role"),
    limit: int = 50,
    db: Session = Depends(get_db)
):
    q = db.query(Player)
    if team:
        q = q.filter(Player.ipl_team == team)
    if role:
        q = q.filter(Player.role == role)
    players = q.limit(limit).all()
    return [
        {
            "id":           p.id,
            "player_id":    p.player_id,
            "name":         p.name,
            "role":         p.role,
            "batting_style":p.batting_style,
            "bowling_style":p.bowling_style,
            "ipl_team":     p.ipl_team,
        }
        for p in players
    ]


@router.get("/{player_id}/stats")
def player_stats(player_id: str, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.player_id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Batting stats
    batting = (
        db.query(
            func.sum(BallEvent.runs_batter).label("total_runs"),
            func.count(BallEvent.id).label("balls_faced"),
            func.sum(func.cast(BallEvent.is_wicket, int)).label("times_dismissed"),
        )
        .filter(BallEvent.batter_id == player.id)
        .first()
    )

    balls_faced = batting.balls_faced or 0
    total_runs  = batting.total_runs or 0
    dismissed   = batting.times_dismissed or 0

    avg = round(total_runs / dismissed, 2) if dismissed > 0 else 0
    sr  = round(total_runs / balls_faced * 100, 2) if balls_faced > 0 else 0

    # Bowling stats
    bowling = (
        db.query(
            func.count(BallEvent.id).label("balls_bowled"),
            func.sum(BallEvent.runs_total).label("runs_conceded"),
            func.sum(func.cast(BallEvent.is_wicket, int)).label("wickets"),
        )
        .filter(BallEvent.bowler_id == player.id)
        .filter(BallEvent.extras_type.notin_(["wides", "noballs"]))
        .first()
    )

    balls_bowled   = bowling.balls_bowled or 0
    runs_conceded  = bowling.runs_conceded or 0
    wickets        = bowling.wickets or 0
    economy        = round(runs_conceded / balls_bowled * 6, 2) if balls_bowled > 0 else 0
    bowling_avg    = round(runs_conceded / wickets, 2) if wickets > 0 else 0

    # Phase-wise batting
    def phase_sr(phase_overs):
        res = (
            db.query(
                func.sum(BallEvent.runs_batter),
                func.count(BallEvent.id),
            )
            .filter(BallEvent.batter_id == player.id)
            .filter(BallEvent.over.in_(phase_overs))
            .first()
        )
        runs = res[0] or 0
        balls = res[1] or 0
        return round(runs / balls * 100, 1) if balls > 0 else 0

    powerplay_sr = phase_sr(range(0, 6))
    middle_sr    = phase_sr(range(6, 15))
    death_sr     = phase_sr(range(15, 20))

    # Dismissal patterns
    dismissals = (
        db.query(BallEvent.dismissal_type, func.count(BallEvent.id))
        .filter(BallEvent.batter_id == player.id)
        .filter(BallEvent.is_wicket == True)
        .group_by(BallEvent.dismissal_type)
        .all()
    )
    dismissal_dict = {d[0]: d[1] for d in dismissals if d[0]}

    return {
        "player": {
            "id":           player.id,
            "name":         player.name,
            "player_id":    player.player_id,
            "role":         player.role,
            "batting_style":player.batting_style,
            "bowling_style":player.bowling_style,
            "ipl_team":     player.ipl_team,
        },
        "batting": {
            "total_runs":    total_runs,
            "balls_faced":   balls_faced,
            "average":       avg,
            "strike_rate":   sr,
            "powerplay_sr":  powerplay_sr,
            "middle_sr":     middle_sr,
            "death_sr":      death_sr,
            "dismissal_pattern": dismissal_dict,
        },
        "bowling": {
            "balls_bowled":  balls_bowled,
            "wickets":       wickets,
            "economy":       economy,
            "average":       bowling_avg,
            "runs_conceded": runs_conceded,
        }
    }
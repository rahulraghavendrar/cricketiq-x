"""
CricketIQ X - Cricsheet IPL Data Ingestion
Parses all IPL JSON match files and loads into PostgreSQL.
Run from project root.
Usage: python scripts/etl_cricsheet.py
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime, date
from typing import Optional

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

os.chdir(Path(__file__).parent.parent / "backend")

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import engine, SessionLocal, Base
from app.models.models import (
    Player, Match, BallEvent, Partnership,
    PitchProfile, CareerStat
)

from tqdm import tqdm

# ── Helpers ────────────────────────────────────────────────────────────────

def get_or_create_player(db: Session, name: str, registry: dict) -> Player:
    player_id = registry.get(name, name.lower().replace(" ", "_"))
    p = db.query(Player).filter(Player.player_id == player_id).first()
    if not p:
        p = Player(
            player_id=player_id,
            name=name,
            role="unknown",
            batting_style="unknown",
            bowling_style="unknown",
        )
        db.add(p)
        db.flush()
    return p


def get_or_create_venue(db: Session, venue_name: str, city: str) -> PitchProfile:
    vname = venue_name.strip() if venue_name else "Unknown"
    v = db.query(PitchProfile).filter(PitchProfile.venue_name == vname).first()
    if not v:
        v = PitchProfile(
            venue_name=vname,
            city=city or "",
            spin_wicket_pct=0.0,
            pace_wicket_pct=0.0,
            avg_first_innings=0.0,
            dew_factor="unknown",
            bounce_index=0.5,
            sample_matches=0,
        )
        db.add(v)
        db.flush()
    return v


def parse_date(d) -> Optional[date]:
    if not d:
        return None
    try:
        if isinstance(d, list):
            d = d[0]
        return datetime.strptime(str(d), "%Y-%m-%d").date()
    except Exception:
        return None


# ── Main ingestion ──────────────────────────────────────────────────────────

def ingest_match(db: Session, filepath: Path) -> bool:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        info = data.get("info", {})

        # Skip non-IPL files
        event_name = info.get("event", {}).get("name", "")
        if "Indian Premier League" not in event_name and "IPL" not in event_name:
            return False

        # ── Build registry: name → unique key ──
        registry = {}
        reg = info.get("registry", {}).get("people", {})
        for name, uid in reg.items():
            registry[name] = uid

        # ── Match record ──
        teams   = info.get("teams", ["Unknown", "Unknown"])
        dates   = info.get("dates", [])
        outcome = info.get("outcome", {})
        toss    = info.get("toss", {})

        match_date = parse_date(dates[0] if dates else None)
        season_raw = info.get("season", "")
        season     = str(season_raw).replace("/", "-") if season_raw else ""

        venue_name = info.get("venue", "Unknown")
        city       = info.get("city", "")
        venue      = get_or_create_venue(db, venue_name, city)

        # Check for duplicate
        file_id = filepath.stem
        existing = db.query(Match).filter(Match.match_id == file_id).first()
        if existing:
            return False

        # Winner
        winner = outcome.get("winner", "")
        result = list(outcome.get("by", {}).keys())[0] if outcome.get("by") else "unknown"
        margin_val = list(outcome.get("by", {}).values())[0] if outcome.get("by") else 0

        match = Match(
            match_id      = file_id,
            venue         = venue_name,
            city          = city,
            date          = match_date,
            season        = season,
            team1         = teams[0] if len(teams) > 0 else "",
            team2         = teams[1] if len(teams) > 1 else "",
            toss_winner   = toss.get("winner", ""),
            toss_decision = toss.get("decision", ""),
            winner        = winner,
            result        = result,
            margin        = int(margin_val) if str(margin_val).isdigit() else 0,
            format        = "T20",
        )
        db.add(match)
        db.flush()

        # ── Ball events ──
        innings_data = data.get("innings", [])
        for inn_idx, innings in enumerate(innings_data):
            batting_team = innings.get("team", "")
            overs_list   = innings.get("overs", [])

            # Track partnership state
            partnership_runs  = 0
            partnership_balls = 0
            last_batter1_id   = None
            last_batter2_id   = None

            for over_data in overs_list:
                over_num    = over_data.get("over", 0)
                deliveries  = over_data.get("deliveries", [])

                for ball_idx, delivery in enumerate(deliveries):
                    batter_name   = delivery.get("batter", "")
                    bowler_name   = delivery.get("bowler", "")
                    non_striker   = delivery.get("non_striker", "")

                    batter_obj    = get_or_create_player(db, batter_name, registry)
                    bowler_obj    = get_or_create_player(db, bowler_name, registry)
                    non_st_obj    = get_or_create_player(db, non_striker, registry) if non_striker else None

                    runs_block    = delivery.get("runs", {})
                    runs_batter   = runs_block.get("batter", 0)
                    runs_extras   = runs_block.get("extras", 0)
                    runs_total    = runs_block.get("total", 0)

                    extras_block  = delivery.get("extras", {})
                    extras_type   = list(extras_block.keys())[0] if extras_block else None

                    # Wicket
                    wickets_list  = delivery.get("wickets", [])
                    is_wicket     = len(wickets_list) > 0
                    dismissal_type= wickets_list[0].get("kind", "") if is_wicket else None

                    # Fielder
                    fielder_id = None
                    if is_wicket:
                        fielders = wickets_list[0].get("fielders", [])
                        if fielders:
                            fname = fielders[0].get("name", "") if isinstance(fielders[0], dict) else fielders[0]
                            if fname:
                                f_obj = get_or_create_player(db, fname, registry)
                                fielder_id = f_obj.id

                    ball = BallEvent(
                        match_id       = match.id,
                        innings        = inn_idx + 1,
                        over           = over_num,
                        ball           = ball_idx + 1,
                        batter_id      = batter_obj.id,
                        bowler_id      = bowler_obj.id,
                        non_striker_id = non_st_obj.id if non_st_obj else None,
                        runs_batter    = runs_batter,
                        runs_extras    = runs_extras,
                        runs_total     = runs_total,
                        extras_type    = extras_type,
                        is_wicket      = is_wicket,
                        dismissal_type = dismissal_type,
                        fielder_id     = fielder_id,
                    )
                    db.add(ball)

                    # Track partnership
                    if last_batter1_id is None:
                        last_batter1_id = batter_obj.id
                        last_batter2_id = non_st_obj.id if non_st_obj else None

                    partnership_runs  += runs_batter
                    partnership_balls += 1

                    if is_wicket and last_batter1_id and last_batter2_id:
                        rr = round(partnership_runs / partnership_balls * 6, 2) if partnership_balls > 0 else 0.0
                        p = Partnership(
                            match_id    = match.id,
                            innings     = inn_idx + 1,
                            batter1_id  = last_batter1_id,
                            batter2_id  = last_batter2_id,
                            runs        = partnership_runs,
                            balls       = partnership_balls,
                            run_rate    = rr,
                            wicket_fell = True,
                        )
                        db.add(p)
                        partnership_runs  = 0
                        partnership_balls = 0
                        last_batter1_id   = batter_obj.id
                        last_batter2_id   = non_st_obj.id if non_st_obj else None

        db.commit()
        return True

    except Exception as e:
        db.rollback()
        print(f"\n  ERROR in {filepath.name}: {e}")
        return False


# ── Venue stats update ──────────────────────────────────────────────────────

def update_venue_stats(db: Session):
    """Recalculate spin/pace wicket percentages and avg first innings per venue."""
    print("\nUpdating venue pitch profiles...")
    venues = db.query(PitchProfile).all()

    for v in tqdm(venues, desc="Venues"):
        # All matches at this venue
        matches = db.query(Match).filter(Match.venue == v.venue_name).all()
        if not matches:
            continue

        match_ids = [m.id for m in matches]
        v.sample_matches = len(match_ids)

        # Total wickets — spin vs pace
        spin_styles = ['Left-arm orthodox','Legbreak','Left-arm wrist-spin',
                       'Offbreak','Right-arm offbreak','Left-arm offbreak',
                       'Slow left-arm orthodox','Slow left-arm chinaman']

        total_wickets = 0
        spin_wickets  = 0

        wicket_events = (db.query(BallEvent)
                         .filter(BallEvent.match_id.in_(match_ids))
                         .filter(BallEvent.is_wicket == True)
                         .all())

        for we in wicket_events:
            total_wickets += 1
            bowler = db.query(Player).filter(Player.id == we.bowler_id).first()
            if bowler and any(s.lower() in (bowler.bowling_style or "").lower() for s in ['spin','offbreak','legbreak','orthodox','chinaman']):
                spin_wickets += 1

        if total_wickets > 0:
            v.spin_wicket_pct = round(spin_wickets / total_wickets * 100, 1)
            v.pace_wicket_pct = round((total_wickets - spin_wickets) / total_wickets * 100, 1)

        # Average first innings score
        first_inn_scores = []
        for m in matches:
            inn1_runs = (db.query(BallEvent)
                         .filter(BallEvent.match_id == m.id)
                         .filter(BallEvent.innings == 1)
                         .all())
            total = sum(b.runs_total for b in inn1_runs)
            if total > 0:
                first_inn_scores.append(total)

        if first_inn_scores:
            v.avg_first_innings = round(sum(first_inn_scores) / len(first_inn_scores), 1)

    db.commit()
    print("Venue stats updated.")


# ── Entry point ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("CricketIQ X — Cricsheet IPL Data Ingestion")
    print("=" * 60)

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables verified.")

    # Find all JSON match files
    data_dir = Path(__file__).parent.parent / "data" / "raw" / "ipl_json"

    if not data_dir.exists():
        print(f"\nERROR: Data directory not found: {data_dir}")
        print("Please download ipl_json.zip from cricsheet.org and extract to data/raw/ipl_json/")
        sys.exit(1)

    match_files = sorted(data_dir.glob("*.json"))
    print(f"Found {len(match_files)} match files.\n")

    if len(match_files) == 0:
        print("No JSON files found. Check your extraction path.")
        sys.exit(1)

    db = SessionLocal()

    loaded   = 0
    skipped  = 0
    errors   = 0

    try:
        for filepath in tqdm(match_files, desc="Loading matches"):
            result = ingest_match(db, filepath)
            if result:
                loaded += 1
            else:
                skipped += 1

    except KeyboardInterrupt:
        print("\nInterrupted by user. Saving progress...")
        db.commit()

    finally:
        # Update venue stats
        update_venue_stats(db)
        db.close()

    print("\n" + "=" * 60)
    print(f"Done!")
    print(f"  Matches loaded  : {loaded}")
    print(f"  Skipped (dupe)  : {skipped}")
    print(f"  Errors          : {errors}")
    print("=" * 60)

    # Final counts
    db2 = SessionLocal()
    print(f"\nDatabase summary:")
    print(f"  Players    : {db2.query(Player).count()}")
    print(f"  Matches    : {db2.query(Match).count()}")
    print(f"  Ball events: {db2.query(BallEvent).count()}")
    print(f"  Partnerships: {db2.query(Partnership).count()}")
    print(f"  Venues     : {db2.query(PitchProfile).count()}")
    db2.close()


if __name__ == "__main__":
    main()
"""
CricketIQ X - Feature Engineering Module
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import text
from tqdm import tqdm


def run_feature_engineering(db, engine):
    from app.models.models import Player, BallEvent, CareerStat
    from app.ml.model_utils import get_bowler_type

    # ── Step 1: Verify classifications are applied ───────────
    print("\nStep 1: Verifying player classifications...")
    spin_count = db.query(Player).filter(
        Player.bowling_style.like('spin%')
    ).count()
    pace_count = db.query(Player).filter(
        Player.bowling_style.like('pace%')
    ).count()
    print(f"  Spin bowlers in DB : {spin_count}")
    print(f"  Pace bowlers in DB : {pace_count}")

    # ── Step 2: Load all ball events with bowler type ────────
    print("\nStep 2: Loading ball events...")
    query = text("""
        SELECT
            be.id,
            be.match_id,
            be.innings,
            be.over,
            be.ball,
            be.batter_id,
            be.bowler_id,
            be.runs_batter,
            be.runs_total,
            be.extras_type,
            be.is_wicket,
            be.dismissal_type,
            p_bat.name          AS batter_name,
            p_bat.role          AS batter_role,
            p_bow.name          AS bowler_name,
            p_bow.bowling_style AS bowler_style,
            m.venue,
            m.season,
            m.winner,
            m.team1,
            m.team2
        FROM ball_events be
        JOIN players p_bat ON be.batter_id = p_bat.id
        JOIN players p_bow ON be.bowler_id = p_bow.id
        JOIN matches m     ON be.match_id  = m.id
        WHERE (be.extras_type NOT IN ('wides', 'noballs')
               OR be.extras_type IS NULL)
    """)
    df = pd.read_sql(query, engine)

    # Classify bowler type from stored style
    df['bowler_type'] = df['bowler_style'].apply(
        lambda s: 'spin' if isinstance(s, str) and 'spin' in s.lower() else 'pace'
    )

    total = len(df)
    spin_balls = (df['bowler_type'] == 'spin').sum()
    pace_balls = (df['bowler_type'] == 'pace').sum()
    print(f"  Loaded {total:,} ball events.")
    print(f"  Spin balls : {spin_balls:,} ({spin_balls/total*100:.1f}%)")
    print(f"  Pace balls : {pace_balls:,} ({pace_balls/total*100:.1f}%)")

    # ── Step 3: Batting features ─────────────────────────────
    print("\nStep 3: Computing batting features...")
    batting_rows = []

    for batter_id, grp in tqdm(df.groupby('batter_id'), desc="  Batters"):
        total_balls = len(grp)
        if total_balls < 30:
            continue

        total_runs    = int(grp['runs_batter'].sum())
        total_wickets = int(grp['is_wicket'].sum())
        batter_name   = grp['batter_name'].iloc[0]

        avg = round(total_runs / total_wickets, 2) if total_wickets > 0 else float(total_runs)
        sr  = round(total_runs / total_balls * 100, 2)

        spin = grp[grp['bowler_type'] == 'spin']
        pace = grp[grp['bowler_type'] == 'pace']

        vs_spin_sr = round(spin['runs_batter'].sum() / len(spin) * 100, 2) if len(spin) > 10 else sr
        vs_pace_sr = round(pace['runs_batter'].sum() / len(pace) * 100, 2) if len(pace) > 10 else sr
        spin_dr    = round(spin['is_wicket'].sum()   / len(spin) * 100, 2) if len(spin) > 10 else 0.0
        pace_dr    = round(pace['is_wicket'].sum()   / len(pace) * 100, 2) if len(pace) > 10 else 0.0

        pp    = grp[grp['over'] < 6]
        mid   = grp[(grp['over'] >= 6) & (grp['over'] < 15)]
        death = grp[grp['over'] >= 15]

        pp_sr    = round(pp['runs_batter'].sum()    / len(pp)    * 100, 2) if len(pp)    > 5 else sr
        mid_sr   = round(mid['runs_batter'].sum()   / len(mid)   * 100, 2) if len(mid)   > 5 else sr
        death_sr = round(death['runs_batter'].sum() / len(death) * 100, 2) if len(death) > 5 else sr

        boundary_pct = round(len(grp[grp['runs_batter'] >= 4]) / total_balls * 100, 2)
        dot_pct      = round(len(grp[grp['runs_batter'] == 0]) / total_balls * 100, 2)

        dismissals    = grp[grp['is_wicket'] == True]['dismissal_type'].value_counts()
        primary_d     = str(dismissals.index[0])  if len(dismissals) > 0 else 'unknown'
        primary_d_pct = round(dismissals.iloc[0] / dismissals.sum() * 100, 1) if len(dismissals) > 0 else 0.0

        pressure_index = round(
            max(0.0, min(1.0, 1.0 - (death_sr / 200.0))) if len(death) > 10 else 0.5, 3
        )

        batting_rows.append({
            'player_id':             int(batter_id),
            'player_name':           batter_name,
            'total_runs':            total_runs,
            'total_balls':           int(total_balls),
            'total_wickets':         total_wickets,
            'average':               float(avg),
            'strike_rate':           float(sr),
            'vs_spin_sr':            float(vs_spin_sr),
            'vs_pace_sr':            float(vs_pace_sr),
            'spin_dismissal_rate':   float(spin_dr),
            'pace_dismissal_rate':   float(pace_dr),
            'powerplay_sr':          float(pp_sr),
            'middle_sr':             float(mid_sr),
            'death_sr':              float(death_sr),
            'boundary_pct':          float(boundary_pct),
            'dot_ball_pct':          float(dot_pct),
            'primary_dismissal':     primary_d,
            'primary_dismissal_pct': float(primary_d_pct),
            'pressure_index':        float(pressure_index),
            'spin_balls_faced':      int(len(spin)),
            'pace_balls_faced':      int(len(pace)),
        })

    batting_df = pd.DataFrame(batting_rows)
    print(f"  Done: {len(batting_df)} batters.")

    # ── Step 4: Bowling features ─────────────────────────────
    print("\nStep 4: Computing bowling features...")
    bowling_rows = []

    for bowler_id, grp in tqdm(df.groupby('bowler_id'), desc="  Bowlers"):
        total_balls = len(grp)
        if total_balls < 30:
            continue

        total_runs    = int(grp['runs_total'].sum())
        total_wickets = int(grp['is_wicket'].sum())
        bowler_name   = grp['bowler_name'].iloc[0]
        bowler_style  = grp['bowler_style'].iloc[0]
        bowler_type   = grp['bowler_type'].iloc[0]

        economy     = round(total_runs / total_balls * 6, 2)
        bowling_avg = round(total_runs / total_wickets, 2) if total_wickets > 0 else 999.0
        wicket_rate = round(total_balls / total_wickets, 1) if total_wickets > 0 else 999.0

        pp    = grp[grp['over'] < 6]
        mid   = grp[(grp['over'] >= 6) & (grp['over'] < 15)]
        death = grp[grp['over'] >= 15]

        pp_eco    = round(pp['runs_total'].sum()    / len(pp)    * 6, 2) if len(pp)    > 0 else economy
        mid_eco   = round(mid['runs_total'].sum()   / len(mid)   * 6, 2) if len(mid)   > 0 else economy
        death_eco = round(death['runs_total'].sum() / len(death) * 6, 2) if len(death) > 0 else economy

        dot_pct       = round(len(grp[grp['runs_total'] == 0]) / total_balls * 100, 2)
        death_dots    = death[death['runs_total'] == 0]
        death_dot_pct = round(len(death_dots) / len(death) * 100, 2) if len(death) > 0 else 0.0
        boundary_pct  = round(len(grp[grp['runs_total'] >= 4]) / total_balls * 100, 2)

        run_dist      = grp['runs_total'].value_counts(normalize=True)
        entropy       = float(-sum(p * np.log2(p + 1e-10) for p in run_dist))
        predictability = round(1.0 - min(entropy / 3.0, 1.0), 3)

        dismissals = grp[grp['is_wicket'] == True]['dismissal_type'].value_counts()
        best_d     = str(dismissals.index[0]) if len(dismissals) > 0 else 'unknown'

        bowling_rows.append({
            'player_id':             int(bowler_id),
            'player_name':           bowler_name,
            'bowler_type':           bowler_type,
            'bowler_subtype':        bowler_style,
            'total_balls':           int(total_balls),
            'total_runs':            int(total_runs),
            'total_wickets':         int(total_wickets),
            'economy':               float(economy),
            'bowling_avg':           float(bowling_avg),
            'wicket_rate':           float(wicket_rate),
            'pp_economy':            float(pp_eco),
            'mid_economy':           float(mid_eco),
            'death_economy':         float(death_eco),
            'pp_wickets':            int(pp['is_wicket'].sum()),
            'mid_wickets':           int(mid['is_wicket'].sum()),
            'death_wickets':         int(death['is_wicket'].sum()),
            'dot_ball_pct':          float(dot_pct),
            'death_dot_pct':         float(death_dot_pct),
            'boundary_pct_conceded': float(boundary_pct),
            'predictability':        float(predictability),
            'best_dismissal_type':   best_d,
        })

    bowling_df = pd.DataFrame(bowling_rows)
    print(f"  Done: {len(bowling_df)} bowlers.")

    # ── Step 5: Save CSVs ────────────────────────────────────
    print("\nStep 5: Saving feature files...")
    output_dir = Path(__file__).parent.parent.parent.parent / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    batting_df.to_csv(output_dir / "batting_features.csv", index=False)
    bowling_df.to_csv(output_dir / "bowling_features.csv", index=False)
    print(f"  batting_features.csv — {len(batting_df)} rows")
    print(f"  bowling_features.csv — {len(bowling_df)} rows")

    # ── Step 6: Save to DB ───────────────────────────────────
    print("\nStep 6: Saving career stats to database...")
    for _, row in tqdm(batting_df.iterrows(), total=len(batting_df), desc="  Saving"):
        existing = db.query(CareerStat).filter(
            CareerStat.player_id == int(row['player_id']),
            CareerStat.season    == 'all'
        ).first()
        if existing:
            existing.runs        = int(row['total_runs'])
            existing.balls_faced = int(row['total_balls'])
            existing.avg         = float(row['average'])
            existing.sr          = float(row['strike_rate'])
        else:
            db.add(CareerStat(
                player_id   = int(row['player_id']),
                season      = 'all',
                runs        = int(row['total_runs']),
                balls_faced = int(row['total_balls']),
                avg         = float(row['average']),
                sr          = float(row['strike_rate']),
            ))
    db.commit()
    print("  Done.")

    return batting_df, bowling_df
"""
CricketIQ X - Apply manual player classifications to database
Run from project root: python scripts/apply_classifications.py
"""

import sys
import os
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
os.chdir(Path(__file__).parent.parent / "backend")

from app.db.database import SessionLocal
from app.models.models import Player, BallEvent

print("=" * 60)
print("CricketIQ X - Applying Player Classifications")
print("=" * 60)

# Load classifications
csv_path = Path(__file__).parent.parent / "data" / "raw" / "player_classifications.csv"
df = pd.read_csv(csv_path)
print(f"Loaded {len(df)} player classifications.")

db = SessionLocal()
players = db.query(Player).all()

# Build a lookup by database ID
id_to_player = {p.id: p for p in players}

updated      = 0
not_found    = 0
spin_count   = 0
pace_count   = 0

role_counts = {}

for _, row in df.iterrows():
    pid = int(row['id'])
    if pid not in id_to_player:
        not_found += 1
        continue

    p = id_to_player[pid]
    p.role          = str(row['role'])
    p.bowling_style = str(row['bowling_type']) if pd.notna(row['bowling_type']) else 'pace'

    # Store subtype in bowling_style as "pace:fast-medium" or "spin:leg-spin"
    subtype = str(row['bowling_subtype']) if pd.notna(row.get('bowling_subtype')) else ''
    if subtype:
        p.bowling_style = f"{row['bowling_type']}:{subtype}"

    if row['bowling_type'] == 'spin':
        spin_count += 1
    else:
        pace_count += 1

    role_counts[p.role] = role_counts.get(p.role, 0) + 1
    updated += 1

# Tag all remaining players as batters or unknown based on activity
all_classified_ids = set(df['id'].tolist())
for p in players:
    if p.id not in all_classified_ids:
        balls_faced  = db.query(BallEvent).filter(BallEvent.batter_id == p.id).count()
        fielded      = db.query(BallEvent).filter(BallEvent.fielder_id == p.id).count()
        balls_bowled = db.query(BallEvent).filter(BallEvent.bowler_id == p.id).count()

        if fielded > 15 and balls_faced > 30:
            p.role = 'wicketkeeper'
        elif balls_faced > 100:
            p.role = 'batter'
        elif balls_bowled > 30:
            p.role = 'bowler'
            p.bowling_style = 'pace:fast-medium'
        else:
            p.role = 'unknown'

        role_counts[p.role] = role_counts.get(p.role, 0) + 1

db.commit()
db.close()

print(f"\nResults:")
print(f"  Updated from CSV   : {updated}")
print(f"  Not found          : {not_found}")
print(f"  Spin bowlers       : {spin_count}")
print(f"  Pace bowlers       : {pace_count}")
print(f"\nRole breakdown:")
for role, count in sorted(role_counts.items()):
    print(f"  {role:20s}: {count}")
print("=" * 60)
print("Done! All players classified.")
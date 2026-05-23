"""
CricketIQ X - Master Training Script
Run from project root: python scripts/train_models.py
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
os.chdir(Path(__file__).parent.parent / "backend")

from app.db.database import SessionLocal, engine
from app.ml.feature_engineering import run_feature_engineering
from app.ml.weakness_detector   import train_weakness_model
from app.ml.matchup_predictor   import train_matchup_model

print("=" * 60)
print("CricketIQ X - Full Model Training Pipeline")
print("=" * 60)

db = SessionLocal()

print("\n[1/3] Feature Engineering...")
batting_df, bowling_df = run_feature_engineering(db, engine)
db.close()

print("\n[2/3] Training Weakness Detector (XGBoost)...")
train_weakness_model()

print("\n[3/3] Training Matchup Predictor (LightGBM)...")
train_matchup_model()

print("\n" + "=" * 60)
print("All models trained and saved to data/models/")
print("=" * 60)
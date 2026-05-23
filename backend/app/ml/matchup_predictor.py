import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import lightgbm as lgb
from app.ml.model_utils import save_model, load_model

FEATURES_DIR = Path(__file__).parent.parent.parent.parent / "data" / "processed"


def build_matchup_features(batting_df, bowling_df):
    records = []
    for _, bat in batting_df.iterrows():
        for _, bow in bowling_df.iterrows():
            if bat['total_balls'] < 50 or bow['total_balls'] < 50:
                continue
            is_spin   = 1 if bow['bowler_type'] == 'spin' else 0
            batter_sr = bat['vs_spin_sr']         if is_spin else bat['vs_pace_sr']
            batter_dr = bat['spin_dismissal_rate'] if is_spin else bat['pace_dismissal_rate']
            bowler_eco = bow['mid_economy']        if is_spin else bow['pp_economy']

            edge = max(0.0, min(1.0,
                (100 - batter_sr) / 100 * 0.3 +
                batter_dr / 20          * 0.3 +
                (12 - bowler_eco) / 12  * 0.2 +
                bow['dot_ball_pct'] / 100 * 0.2
            ))

            records.append({
                'batter_sr':             bat['strike_rate'],
                'batter_avg':            bat['average'],
                'batter_vs_type_sr':     batter_sr,
                'batter_dr_vs_type':     batter_dr,
                'batter_pp_sr':          bat['powerplay_sr'],
                'batter_death_sr':       bat['death_sr'],
                'batter_boundary_pct':   bat['boundary_pct'],
                'batter_pressure_index': bat['pressure_index'],
                'bowler_economy':        bow['economy'],
                'bowler_pp_eco':         bow['pp_economy'],
                'bowler_mid_eco':        bow['mid_economy'],
                'bowler_death_eco':      bow['death_economy'],
                'bowler_dot_pct':        bow['dot_ball_pct'],
                'bowler_wicket_rate':    min(bow['wicket_rate'], 100),
                'bowler_predictability': bow['predictability'],
                'bowler_is_spin':        is_spin,
                'label':                 1 if edge > 0.5 else 0,
            })
    return pd.DataFrame(records)


def train_matchup_model():
    batting_df = pd.read_csv(FEATURES_DIR / "batting_features.csv")
    bowling_df = pd.read_csv(FEATURES_DIR / "bowling_features.csv")

    print("  Building matchup matrix...")
    bat_s = batting_df.sample(min(80, len(batting_df)), random_state=42)
    bow_s = bowling_df.sample(min(60, len(bowling_df)), random_state=42)
    df    = build_matchup_features(bat_s, bow_s)
    print(f"  Built {len(df):,} matchup records.")

    if len(df) == 0:
        print("  WARNING: No matchup records built — skipping matchup model")
        return None, []

    feature_cols = [c for c in df.columns if c != 'label']
    X = df[feature_cols].fillna(0)
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = lgb.LGBMClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        num_leaves=31,
        subsample=0.8,
        random_state=42,
        n_jobs=-1,
        verbose=-1,
    )
    model.fit(X_train, y_train)

    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    print(f"  Matchup model ROC-AUC: {auc:.3f}")

    save_model(model,        "matchup_predictor")
    save_model(feature_cols, "matchup_feature_cols")
    return model, feature_cols


def predict_matchup(batting_features: dict, bowling_features: dict, phase: str = "middle") -> dict:
    try:
        model        = load_model("matchup_predictor")
        feature_cols = load_model("matchup_feature_cols")
    except FileNotFoundError:
        return {"error": "Model not trained yet"}

    is_spin   = 1 if bowling_features.get('bowler_type', 'pace') == 'spin' else 0
    batter_sr = batting_features.get('vs_spin_sr' if is_spin else 'vs_pace_sr', 100)
    batter_dr = batting_features.get(
        'spin_dismissal_rate' if is_spin else 'pace_dismissal_rate', 5
    )

    features = {
        'batter_sr':             batting_features.get('strike_rate', 100),
        'batter_avg':            batting_features.get('average', 30),
        'batter_vs_type_sr':     batter_sr,
        'batter_dr_vs_type':     batter_dr,
        'batter_pp_sr':          batting_features.get('powerplay_sr', 120),
        'batter_death_sr':       batting_features.get('death_sr', 130),
        'batter_boundary_pct':   batting_features.get('boundary_pct', 15),
        'batter_pressure_index': batting_features.get('pressure_index', 0.5),
        'bowler_economy':        bowling_features.get('economy', 8),
        'bowler_pp_eco':         bowling_features.get('pp_economy', 8),
        'bowler_mid_eco':        bowling_features.get('mid_economy', 8),
        'bowler_death_eco':      bowling_features.get('death_economy', 9),
        'bowler_dot_pct':        bowling_features.get('dot_ball_pct', 35),
        'bowler_wicket_rate':    min(bowling_features.get('wicket_rate', 20), 100),
        'bowler_predictability': bowling_features.get('predictability', 0.5),
        'bowler_is_spin':        is_spin,
    }

    X     = pd.DataFrame([[features.get(c, 0) for c in feature_cols]], columns=feature_cols)
    proba = model.predict_proba(X)[0]

    bowler_edge = round(float(proba[1]) * 100, 1)
    batter_edge = round(float(proba[0]) * 100, 1)

    return {
        'advantage':       'bowler' if bowler_edge > 50 else 'batter',
        'bowler_edge_pct': bowler_edge,
        'batter_edge_pct': batter_edge,
        'recommended_delivery': (
            'Toss up outside off — invite the drive' if is_spin and bowler_edge > 60
            else 'Short of length — hit the deck'    if not is_spin and bowler_edge > 60
            else 'Mix deliveries — batter in control'
        ),
    }
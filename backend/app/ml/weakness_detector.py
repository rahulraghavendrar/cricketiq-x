import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import xgboost as xgb
from app.ml.model_utils import save_model, load_model

FEATURES_DIR = Path(__file__).parent.parent.parent.parent / "data" / "processed"


def get_weakness_label(row) -> str:
    spin_dr  = row.get('spin_dismissal_rate', 0)
    pace_dr  = row.get('pace_dismissal_rate', 0)
    death_sr = row.get('death_sr', 100)
    pressure = row.get('pressure_index', 0.5)
    vs_spin  = row.get('vs_spin_sr', 100)
    vs_pace  = row.get('vs_pace_sr', 100)

    if spin_dr > pace_dr * 1.3 and vs_spin < 100:
        return 'spin_weak'
    elif pace_dr > spin_dr * 1.3 and vs_pace < 100:
        return 'pace_weak'
    elif death_sr < 120:
        return 'death_weak'
    elif pressure > 0.6:
        return 'pressure_weak'
    else:
        return 'balanced'


def train_weakness_model():
    path = FEATURES_DIR / "batting_features.csv"
    if not path.exists():
        raise FileNotFoundError("Run train_models.py first to generate features")

    df = pd.read_csv(path)
    print(f"  Training on {len(df)} players...")

    df['weakness_label'] = df.apply(get_weakness_label, axis=1)
    print("  Label distribution:")
    for label, count in df['weakness_label'].value_counts().items():
        print(f"    {label}: {count}")

    feature_cols = [
        'vs_spin_sr', 'vs_pace_sr',
        'spin_dismissal_rate', 'pace_dismissal_rate',
        'powerplay_sr', 'middle_sr', 'death_sr',
        'boundary_pct', 'dot_ball_pct',
        'pressure_index', 'primary_dismissal_pct',
        'strike_rate', 'average',
        'spin_balls_faced', 'pace_balls_faced',
    ]
    feature_cols = [c for c in feature_cols if c in df.columns]

    X         = df[feature_cols].fillna(0)
    y         = df['weakness_label']
    le        = LabelEncoder()
    y_encoded = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric='mlogloss',
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    y_pred = model.predict(X_test)
    print("\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    save_model(model,        "weakness_detector")
    save_model(le,           "weakness_label_encoder")
    save_model(feature_cols, "weakness_feature_cols")

    return model, le, feature_cols


def predict_weakness(player_features: dict) -> dict:
    try:
        model        = load_model("weakness_detector")
        le           = load_model("weakness_label_encoder")
        feature_cols = load_model("weakness_feature_cols")
    except FileNotFoundError:
        return {"error": "Model not trained yet"}

    X = pd.DataFrame(
        [[player_features.get(col, 0) for col in feature_cols]],
        columns=feature_cols
    )

    proba      = model.predict_proba(X)[0]
    pred_idx   = proba.argmax()
    label      = le.classes_[pred_idx]
    confidence = round(float(proba[pred_idx]) * 100, 1)

    all_probs = {
        le.classes_[i]: round(float(p) * 100, 1)
        for i, p in enumerate(proba)
    }

    advice_map = {
        'spin_weak':     {
            'delivery': 'Off-spin or leg-spin outside off stump',
            'field':    'Slip, silly point, short leg, long on',
            'phase':    'Middle overs 7-15'
        },
        'pace_weak':     {
            'delivery': 'Short pitched, 5th stump line',
            'field':    'Fine leg, gully, deep backward square',
            'phase':    'Powerplay or death overs'
        },
        'death_weak':    {
            'delivery': 'Yorker length, full and straight',
            'field':    'Long on, long off, fine leg, deep midwicket',
            'phase':    'Death overs 17-20'
        },
        'pressure_weak': {
            'delivery': 'Dot ball pressure, target the stumps',
            'field':    'Attacking field — slip, mid on up',
            'phase':    'Any phase when wickets have fallen'
        },
        'balanced':      {
            'delivery': 'Mix pace and spin based on matchup data',
            'field':    'Standard field, adjust per phase',
            'phase':    'All phases'
        },
    }

    return {
        'weakness_label':    label,
        'confidence_pct':    confidence,
        'all_probabilities': all_probs,
        'tactical_advice':   advice_map.get(label, {}),
    }
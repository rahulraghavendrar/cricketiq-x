import joblib
import pandas as pd
from pathlib import Path

MODELS_DIR = Path(__file__).parent.parent.parent.parent / "data" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def get_bowler_type(bowling_style: str) -> str:
    """
    Extract spin or pace from stored bowling_style.
    Handles formats like 'spin:leg-spin' or 'pace:fast-medium' or plain 'spin'/'pace'.
    """
    if not bowling_style or bowling_style == 'unknown':
        return 'pace'
    return 'spin' if 'spin' in bowling_style.lower() else 'pace'


def get_bowling_subtype(bowling_style: str) -> str:
    """Extract subtype e.g. 'leg-spin', 'fast-medium', 'off-spin'."""
    if not bowling_style or ':' not in bowling_style:
        return 'unknown'
    return bowling_style.split(':', 1)[1]


def save_model(model, name: str):
    path = MODELS_DIR / f"{name}.joblib"
    joblib.dump(model, path)
    print(f"  Saved: {name}.joblib")
    return path


def load_model(name: str):
    path = MODELS_DIR / f"{name}.joblib"
    if not path.exists():
        raise FileNotFoundError(f"Model not found: {path}")
    return joblib.load(path)
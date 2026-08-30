from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Project root (backend/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Dataset path
DATASET_PATH = BASE_DIR / "app" / "database" / "water_quality.csv"

# Model save path
MODEL_PATH = BASE_DIR / "app" / "ai" / "water_quality_model.pkl"

# Load dataset
df = pd.read_csv(DATASET_PATH)

X = df[
    [
        "temperature",
        "ph",
        "salinity",
        "dissolved_oxygen",
    ]
]

y = df["quality"]

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
)

model.fit(X, y)

# Save model
joblib.dump(model, MODEL_PATH)

print("✅ Model trained successfully!")
print(f"Saved at: {MODEL_PATH}")
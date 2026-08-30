from pathlib import Path

import joblib

# Get the directory where this file is located
BASE_DIR = Path(__file__).resolve().parent

# Path to the trained model
MODEL_PATH = BASE_DIR / "water_quality_model.pkl"

# Load the model
model = joblib.load(MODEL_PATH)


def predict_ml(
    temperature: float,
    ph: float,
    salinity: float,
    dissolved_oxygen: float,
):
    prediction = model.predict(
        [[
            temperature,
            ph,
            salinity,
            dissolved_oxygen,
        ]]
    )[0]

    return {
        "prediction": prediction
    }
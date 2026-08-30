def predict_water_quality(
    temperature: float,
    ph: float,
    salinity: float,
    dissolved_oxygen: float
):

    score = 0

    if 20 <= temperature <= 30:
        score += 1

    if 6.5 <= ph <= 8.5:
        score += 1

    if 30 <= salinity <= 36:
        score += 1

    if dissolved_oxygen >= 5:
        score += 1

    if score == 4:
        quality = "Good"
        pollution = "Low"
        recommendation = "Water is safe for marine life."

    elif score >= 2:
        quality = "Moderate"
        pollution = "Medium"
        recommendation = "Continuous monitoring recommended."

    else:
        quality = "Poor"
        pollution = "High"
        recommendation = "Immediate action required."

    return {
        "water_quality": quality,
        "pollution_level": pollution,
        "recommendation": recommendation
    }

import joblib
import os

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "ocean_model.pkl",
)

model = joblib.load(MODEL_PATH)


class OceanPredictor:

    @staticmethod
    def predict(
        temperature: float,
        ph: float,
        salinity: float,
        oxygen: float,
    ):

        prediction = model.predict([
            [
                temperature,
                ph,
                salinity,
                oxygen,
            ]
        ])

        return prediction[0]
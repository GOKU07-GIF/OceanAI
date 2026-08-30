from app.ai.predictor import OceanPredictor
from app.external.marine_api import MarineAPI


class AIService:
    """
    Service for handling AI-related operations.
    """

    @staticmethod
    def analyze_live_location(
        latitude: float,
        longitude: float,
    ) -> dict:

        marine_data = MarineAPI.get_current_data(
            latitude=latitude,
            longitude=longitude,
        )

        prediction = OceanPredictor.predict(
            temperature=marine_data["temperature"],
            ph=8.1,
            salinity=34.5,
            oxygen=6.2,
        )

        return {
            "latitude": marine_data["latitude"],
            "longitude": marine_data["longitude"],
            "time": marine_data["time"],
            "temperature": marine_data["temperature"],
            "prediction": prediction,
            "source": "Open-Meteo Marine API",
        }
import requests


class MarineAPI:
    """
    Fetch live marine data from Open-Meteo Marine API.
    """

    BASE_URL = "https://marine-api.open-meteo.com/v1/marine"

    @staticmethod
    def get_current_data(
        latitude: float,
        longitude: float,
    ) -> dict:

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "sea_surface_temperature",
        }

        response = requests.get(
            MarineAPI.BASE_URL,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        return {
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "temperature": data["current"]["sea_surface_temperature"],
            "time": data["current"]["time"],
        }
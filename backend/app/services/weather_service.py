import requests

from app.core.config import settings
from app.core.logger import logger

API_KEY = settings.WEATHER_API_KEY

BASE_URL = "https://api.weatherapi.com/v1/current.json"


def get_weather(city: str):
    """
    Fetch real-time weather data for a given city.
    """

    if not API_KEY:
        logger.error("Weather API key is not configured.")

        return {
            "error": "Weather API key is not configured."
        }

    params = {
        "key": API_KEY,
        "q": city,
        "aqi": "no"
    }

    try:
        logger.info(f"Fetching weather for {city}")

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        logger.info(f"Weather fetched successfully for {city}")

        return {
            "city": data["location"]["name"],
            "region": data["location"]["region"],
            "country": data["location"]["country"],
            "temperature": data["current"]["temp_c"],
            "humidity": data["current"]["humidity"],
            "wind_speed": data["current"]["wind_kph"],
            "condition": data["current"]["condition"]["text"],
            "icon": "https:" + data["current"]["condition"]["icon"],
            "last_updated": data["current"]["last_updated"]
        }

    except requests.exceptions.Timeout:
        logger.error(f"Weather API timeout for {city}")

        return {
            "error": "Weather service timed out."
        }

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e}")

        return {
            "error": f"HTTP Error: {e}",
            "details": response.text
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Request Error: {e}")

        return {
            "error": f"Request Error: {e}"
        }

    except Exception:
        logger.exception(
            f"Unexpected error while fetching weather for {city}"
        )

        return {
            "error": "Internal Server Error"
        }
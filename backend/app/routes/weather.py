from fastapi import APIRouter

from app.services.weather_service import get_weather

router = APIRouter(
    prefix="/weather",
    tags=["Weather"]
)


@router.get("/{city}")
def weather(city: str):
    return get_weather(city)
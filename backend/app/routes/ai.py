from fastapi import APIRouter

from app.services.ai_service import AIService

router = APIRouter(
    prefix="/ai",
    tags=["AI Analysis"],
)


@router.get("/live-analysis")
def live_analysis(
    latitude: float,
    longitude: float,
):
    return AIService.analyze_live_location(
        latitude=latitude,
        longitude=longitude,
    )
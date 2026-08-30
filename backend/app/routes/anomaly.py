from fastapi import APIRouter

from app.ai.anomaly_detector import detect_anomaly
from app.schemas.anomaly_schema import (
    AnomalyRequest,
    AnomalyResponse,
)

router = APIRouter(
    prefix="/anomaly",
    tags=["Anomaly Detection"]
)


@router.post(
    "/detect",
    response_model=AnomalyResponse
)
def detect(data: AnomalyRequest):

    return detect_anomaly(
        data.temperature,
        data.ph,
        data.salinity,
        data.dissolved_oxygen
    )
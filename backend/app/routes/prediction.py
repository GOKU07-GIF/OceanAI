from fastapi import APIRouter

from app.ai.predictor import predict_water_quality
from app.ai.ml_predictor import predict_ml

from app.schemas.prediction_schema import (
    PredictionRequest,
    PredictionResponse,
)

router = APIRouter(
    prefix="/prediction",
    tags=["Prediction"],
)


# Rule-Based AI Prediction
@router.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(data: PredictionRequest):
    return predict_water_quality(
        data.temperature,
        data.ph,
        data.salinity,
        data.dissolved_oxygen,
    )


# Machine Learning Prediction
@router.post("/ml")
def ml_predict(data: PredictionRequest):
    return predict_ml(
        data.temperature,
        data.ph,
        data.salinity,
        data.dissolved_oxygen,
    )
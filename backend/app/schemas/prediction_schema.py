from pydantic import BaseModel


class PredictionRequest(BaseModel):
    temperature: float
    ph: float
    salinity: float
    dissolved_oxygen: float


class PredictionResponse(BaseModel):
    water_quality: str
    pollution_level: str
    recommendation: str
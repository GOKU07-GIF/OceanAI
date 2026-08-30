from pydantic import BaseModel
from typing import List


class AnomalyRequest(BaseModel):
    temperature: float
    ph: float
    salinity: float
    dissolved_oxygen: float


class AnomalyResponse(BaseModel):
    status: str
    alerts: List[str]
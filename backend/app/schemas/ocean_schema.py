from datetime import datetime
from pydantic import BaseModel


class OceanDataCreate(BaseModel):
    latitude: float
    longitude: float
    temperature: float
    ph: float
    salinity: float
    oxygen: float


class OceanDataUpdate(BaseModel):
    latitude: float
    longitude: float
    temperature: float
    ph: float
    salinity: float
    oxygen: float
    is_active: bool


class OceanDataResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    temperature: float
    ph: float
    salinity: float
    oxygen: float
    is_active: bool
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True
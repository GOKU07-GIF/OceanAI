from datetime import datetime

from pydantic import BaseModel, Field


class SensorReadingCreate(BaseModel):

    sensor_device_id: int = Field(gt=0)

    temperature: float = Field(ge=-5, le=50)
    ph: float = Field(ge=0, le=14)
    salinity: float = Field(ge=0, le=50)
    oxygen: float = Field(ge=0, le=20)
    turbidity: float = Field(ge=0, le=10000)
    water_quality: float = Field(ge=0, le=100)


class SensorReadingResponse(BaseModel):

    id: int
    sensor_device_id: int
    temperature: float
    ph: float
    salinity: float
    oxygen: float
    turbidity: float
    water_quality: float
    created_at: datetime

    class Config:
        from_attributes = True

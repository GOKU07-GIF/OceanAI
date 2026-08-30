from datetime import datetime

from pydantic import BaseModel


class SensorReadingCreate(BaseModel):

    sensor_device_id: int

    temperature: float

    ph: float

    salinity: float

    oxygen: float

    turbidity: float

    water_quality: float


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
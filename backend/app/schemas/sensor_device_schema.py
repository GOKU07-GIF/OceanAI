from datetime import datetime

from pydantic import BaseModel, Field


class SensorDeviceCreate(BaseModel):

    device_id: str = Field(
        min_length=3,
        max_length=100,
    )

    device_name: str = Field(
        min_length=3,
        max_length=100,
    )

    device_type: str

    latitude: float

    longitude: float


class SensorDeviceResponse(BaseModel):

    id: int

    device_id: str

    device_name: str

    device_type: str

    latitude: float

    longitude: float

    firmware_version: str

    battery_level: float

    status: str

    is_active: bool

    created_at: datetime

    class Config:
        from_attributes = True
from datetime import datetime

from pydantic import BaseModel


# ============================================================
# SOS CREATE
# ============================================================

class SOSCreate(BaseModel):
    latitude: float
    longitude: float


# ============================================================
# SOS STATUS UPDATE
# ============================================================

class SOSStatusUpdate(BaseModel):
    status: str


# ============================================================
# ASSIGNED STATION DETAILS
# ============================================================

class SOSStationResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    is_active: bool

    class Config:
        from_attributes = True


# ============================================================
# SOS RESPONSE
# ============================================================

class SOSResponse(BaseModel):
    id: int

    latitude: float
    longitude: float

    user_id: int

    station_id: int | None
    station_distance_km: float | None

    station: SOSStationResponse | None = None

    status: str
    created_at: datetime

    class Config:
        from_attributes = True
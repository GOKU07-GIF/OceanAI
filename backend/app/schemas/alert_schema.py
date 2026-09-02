from datetime import datetime

from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=2000)
    alert_type: str = Field(min_length=1, max_length=50)
    severity: str = Field(min_length=1, max_length=20)
    sos_id: int | None = Field(default=None, gt=0)


class AlertResponse(BaseModel):
    id: int
    title: str
    message: str
    alert_type: str
    severity: str
    is_read: bool
    user_id: int | None
    sos_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True


class AlertReadResponse(BaseModel):
    message: str

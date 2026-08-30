from datetime import datetime

from pydantic import BaseModel


# ============================================================
# CREATE ALERT
# ============================================================

class AlertCreate(BaseModel):
    title: str
    message: str
    alert_type: str
    severity: str

    user_id: int | None = None
    sos_id: int | None = None


# ============================================================
# ALERT RESPONSE
# ============================================================

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


# ============================================================
# MARK ALERT AS READ RESPONSE
# ============================================================

class AlertReadResponse(BaseModel):
    message: str
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.alert_schema import (
    AlertCreate,
    AlertResponse,
    AlertReadResponse,
)

from app.services.alert_service import AlertService


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


# ============================================================
# CREATE ALERT
# ============================================================

@router.post(
    "/",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
):
    return AlertService.create_alert(
        db=db,
        title=alert_data.title,
        message=alert_data.message,
        alert_type=alert_data.alert_type,
        severity=alert_data.severity,
        user_id=alert_data.user_id,
        sos_id=alert_data.sos_id,
    )


# ============================================================
# GET ALL ALERTS
# ============================================================

@router.get(
    "/",
    response_model=list[AlertResponse],
)
def get_all_alerts(
    db: Session = Depends(get_db),
):
    return AlertService.get_all_alerts(db)


# ============================================================
# GET ALERT BY ID
# ============================================================

@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
)
def get_alert_by_id(
    alert_id: int,
    db: Session = Depends(get_db),
):
    return AlertService.get_alert_by_id(
        db,
        alert_id,
    )


# ============================================================
# GET ALERTS FOR USER
# ============================================================

@router.get(
    "/user/{user_id}",
    response_model=list[AlertResponse],
)
def get_user_alerts(
    user_id: int,
    db: Session = Depends(get_db),
):
    return AlertService.get_user_alerts(
        db,
        user_id,
    )


# ============================================================
# GET UNREAD ALERTS FOR USER
# ============================================================

@router.get(
    "/user/{user_id}/unread",
    response_model=list[AlertResponse],
)
def get_unread_user_alerts(
    user_id: int,
    db: Session = Depends(get_db),
):
    return AlertService.get_unread_user_alerts(
        db,
        user_id,
    )


# ============================================================
# MARK ONE ALERT AS READ
# ============================================================

@router.put(
    "/{alert_id}/read",
    response_model=AlertResponse,
)
def mark_alert_as_read(
    alert_id: int,
    db: Session = Depends(get_db),
):
    return AlertService.mark_alert_as_read(
        db,
        alert_id,
    )


# ============================================================
# MARK ALL USER ALERTS AS READ
# ============================================================

@router.put(
    "/user/{user_id}/read-all",
    response_model=AlertReadResponse,
)
def mark_all_user_alerts_as_read(
    user_id: int,
    db: Session = Depends(get_db),
):
    return AlertService.mark_all_user_alerts_as_read(
        db,
        user_id,
    )
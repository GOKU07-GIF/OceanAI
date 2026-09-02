from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models.user import User
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


@router.post(
    "/",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AlertService.create_alert(
        db=db,
        title=alert_data.title,
        message=alert_data.message,
        alert_type=alert_data.alert_type,
        severity=alert_data.severity,
        user_id=current_user.id,
        sos_id=alert_data.sos_id,
    )


@router.get(
    "/",
    response_model=list[AlertResponse],
)
def get_all_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AlertService.get_user_alerts(db, current_user.id)


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
)
def get_alert_by_id(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AlertService.get_alert_by_id(db, alert_id, current_user.id)


@router.get(
    "/user/{user_id}",
    response_model=list[AlertResponse],
)
def get_user_alerts(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id != current_user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="You can only access your own alerts")
    return AlertService.get_user_alerts(db, user_id)


@router.get(
    "/user/{user_id}/unread",
    response_model=list[AlertResponse],
)
def get_unread_user_alerts(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id != current_user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="You can only access your own alerts")
    return AlertService.get_unread_user_alerts(db, user_id)


@router.put(
    "/{alert_id}/read",
    response_model=AlertResponse,
)
def mark_alert_as_read(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AlertService.mark_alert_as_read(db, alert_id, current_user.id)


@router.put(
    "/user/{user_id}/read-all",
    response_model=AlertReadResponse,
)
def mark_all_user_alerts_as_read(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id != current_user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="You can only update your own alerts")
    return AlertService.mark_all_user_alerts_as_read(db, user_id)

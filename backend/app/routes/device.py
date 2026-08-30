from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.core.security import get_current_user

from app.models.user import User

from app.schemas.sensor_device_schema import (
    SensorDeviceCreate,
    SensorDeviceResponse,
)

from app.services.sensor_device_service import (
    create_device,
    get_all_devices,
    get_device,
)

router = APIRouter(
    prefix="/devices",
    tags=["Sensor Devices"],
)


@router.post(
    "",
    response_model=SensorDeviceResponse,
)
def register_device(
    device: SensorDeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_device(
        db=db,
        owner_id=current_user.id,
        device_id=device.device_id,
        device_name=device.device_name,
        device_type=device.device_type,
        latitude=device.latitude,
        longitude=device.longitude,
    )


@router.get(
    "",
    response_model=list[SensorDeviceResponse],
)
def get_devices(
    db: Session = Depends(get_db),
):
    return get_all_devices(
        db,
    )


@router.get(
    "/{device_id}",
    response_model=SensorDeviceResponse,
)
def get_single_device(
    device_id: int,
    db: Session = Depends(get_db),
):
    return get_device(
        db,
        device_id,
    )
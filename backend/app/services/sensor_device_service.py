from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.sensor_device import SensorDevice
from app.repositories.sensor_device_repository import (
    SensorDeviceRepository,
)


def create_device(
    db: Session,
    owner_id: int,
    device_id: str,
    device_name: str,
    device_type: str,
    latitude: float,
    longitude: float,
):
    """
    Register a new sensor device.
    """

    existing = SensorDeviceRepository.get_by_device_id(
        db,
        device_id,
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Device ID already exists",
        )

    device = SensorDevice(
        owner_id=owner_id,
        device_id=device_id,
        device_name=device_name,
        device_type=device_type,
        latitude=latitude,
        longitude=longitude,
    )

    return SensorDeviceRepository.create(
        db,
        device,
    )


def get_all_devices(
    db: Session,
):
    """
    Return all registered devices.
    """
    return SensorDeviceRepository.get_all(
        db,
    )


def get_device(
    db: Session,
    device_id: int,
):
    """
    Return one device.
    """

    device = SensorDeviceRepository.get_by_id(
        db,
        device_id,
    )

    if device is None:
        raise HTTPException(
            status_code=404,
            detail="Device not found",
        )

    return device
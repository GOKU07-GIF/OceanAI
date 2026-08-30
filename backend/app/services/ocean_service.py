from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.ocean_data import OceanData
from app.repositories.ocean_repository import OceanRepository


class OceanService:
    """
    Business logic for Ocean Data.
    """

    @staticmethod
    def create_ocean_data(
        db: Session,
        latitude: float,
        longitude: float,
        temperature: float,
        ph: float,
        salinity: float,
        oxygen: float,
        owner_id: int,
    ):
        ocean = OceanData(
            latitude=latitude,
            longitude=longitude,
            temperature=temperature,
            ph=ph,
            salinity=salinity,
            oxygen=oxygen,
            owner_id=owner_id,
        )

        return OceanRepository.create(
            db,
            ocean,
        )

    @staticmethod
    def get_all_ocean_data(
        db: Session,
    ):
        return OceanRepository.get_all(db)

    @staticmethod
    def get_ocean_data_by_id(
        db: Session,
        ocean_id: int,
    ):
        ocean = OceanRepository.get_by_id(
            db,
            ocean_id,
        )

        if ocean is None:
            raise HTTPException(
                status_code=404,
                detail="Ocean data not found",
            )

        return ocean

    @staticmethod
    def update_ocean_data(
        db: Session,
        ocean_id: int,
        latitude: float,
        longitude: float,
        temperature: float,
        ph: float,
        salinity: float,
        oxygen: float,
        is_active: bool,
    ):
        ocean = OceanRepository.get_by_id(
            db,
            ocean_id,
        )

        if ocean is None:
            raise HTTPException(
                status_code=404,
                detail="Ocean data not found",
            )

        ocean.latitude = latitude
        ocean.longitude = longitude
        ocean.temperature = temperature
        ocean.ph = ph
        ocean.salinity = salinity
        ocean.oxygen = oxygen
        ocean.is_active = is_active

        return OceanRepository.update(
            db,
            ocean,
        )

    @staticmethod
    def delete_ocean_data(
        db: Session,
        ocean_id: int,
    ):
        ocean = OceanRepository.get_by_id(
            db,
            ocean_id,
        )

        if ocean is None:
            raise HTTPException(
                status_code=404,
                detail="Ocean data not found",
            )

        OceanRepository.delete(
            db,
            ocean,
        )

        return {
            "message": "Ocean data deleted successfully"
        }
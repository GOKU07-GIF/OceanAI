from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.ocean_schema import (
    OceanDataCreate,
    OceanDataUpdate,
    OceanDataResponse,
)
from app.services import ocean_service


router = APIRouter(
    prefix="/ocean-data",
    tags=["Ocean Data"],
)


# ============================================================
# CREATE OCEAN DATA
# ============================================================

@router.post("", response_model=OceanDataResponse)
def create_ocean_data(
    data: OceanDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ocean_service.create_ocean_data(
        db=db,
        latitude=data.latitude,
        longitude=data.longitude,
        temperature=data.temperature,
        ph=data.ph,
        salinity=data.salinity,
        oxygen=data.oxygen,
        owner_id=current_user.id,
    )


# ============================================================
# GET ALL OCEAN DATA
# ============================================================

@router.get("", response_model=List[OceanDataResponse])
def get_all_ocean_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ocean_service.get_all_ocean_data(db)


# ============================================================
# GET OCEAN DATA BY ID
# ============================================================

@router.get("/{ocean_id}", response_model=OceanDataResponse)
def get_ocean_data(
    ocean_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ocean_service.get_ocean_data_by_id(
        db,
        ocean_id,
    )


# ============================================================
# UPDATE OCEAN DATA
# ============================================================

@router.put("/{ocean_id}", response_model=OceanDataResponse)
def update_ocean_data(
    ocean_id: int,
    data: OceanDataUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ocean_service.update_ocean_data(
        db=db,
        ocean_id=ocean_id,
        latitude=data.latitude,
        longitude=data.longitude,
        temperature=data.temperature,
        ph=data.ph,
        salinity=data.salinity,
        oxygen=data.oxygen,
        is_active=data.is_active,
    )


# ============================================================
# DELETE OCEAN DATA
# ============================================================

@router.delete("/{ocean_id}")
def delete_ocean_data(
    ocean_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ocean_service.delete_ocean_data(
        db=db,
        ocean_id=ocean_id,
    )

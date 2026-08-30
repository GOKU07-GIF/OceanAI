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
    tags=["Ocean Data"]
)


# Create Ocean Data
@router.post("")
def create_ocean_data(
    data: OceanDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ocean = ocean_service.create_ocean_data(
        db=db,
        location=data.location,
        temperature=data.temperature,
        ph=data.ph,
        owner_id=current_user.id,
    )

    return {
        "message": "Ocean data inserted successfully",
        "id": ocean.id,
    }


# Get All Ocean Data
@router.get("", response_model=List[OceanDataResponse])
def get_all_ocean_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ocean_service.get_all_ocean_data(db)


# Get Ocean Data By ID
@router.get("/{ocean_id}", response_model=OceanDataResponse)
def get_ocean_data(
    ocean_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ocean_service.get_ocean_data(db, ocean_id)


# Update Ocean Data
@router.put("/{ocean_id}")
def update_ocean_data(
    ocean_id: int,
    data: OceanDataUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ocean_service.update_ocean_data(
        db=db,
        ocean_id=ocean_id,
        location=data.location,
        temperature=data.temperature,
        ph=data.ph,
        current_user=current_user,
    )

    return {
        "message": "Ocean data updated successfully",
    }


# Delete Ocean Data
@router.delete("/{ocean_id}")
def delete_ocean_data(
    ocean_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ocean_service.delete_ocean_data(
        db=db,
        ocean_id=ocean_id,
        current_user=current_user,
    )

    return {
        "message": "Ocean data deleted successfully",
    }
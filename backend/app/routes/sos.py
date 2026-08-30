from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.security import get_current_user
from app.models.user import User

from app.schemas.sos_schema import (
    SOSCreate,
    SOSStatusUpdate,
    SOSResponse,
)

from app.services.sos_service import SOSService


router = APIRouter(
    prefix="/sos",
    tags=["SOS"],
)


# ============================================================
# CREATE SOS
# ============================================================

@router.post(
    "/",
    response_model=SOSResponse,
)
def create_sos(
    sos: SOSCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SOSService.create_sos(
        db=db,
        latitude=sos.latitude,
        longitude=sos.longitude,
        user_id=current_user.id,
    )


# ============================================================
# GET ALL SOS REQUESTS
# ============================================================

@router.get(
    "/",
    response_model=list[SOSResponse],
)
def get_all_sos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SOSService.get_all_sos(db)


# ============================================================
# GET SOS BY ID
# ============================================================

@router.get(
    "/{sos_id}",
    response_model=SOSResponse,
)
def get_sos(
    sos_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SOSService.get_sos_by_id(
        db=db,
        sos_id=sos_id,
    )

# ============================================================
# UPDATE SOS STATUS
# ============================================================

@router.put(
    "/{sos_id}/status",
    response_model=SOSResponse,
)
def update_sos_status(
    sos_id: int,
    sos: SOSStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SOSService.update_sos_status(
        db=db,
        sos_id=sos_id,
        status=sos.status,
    )
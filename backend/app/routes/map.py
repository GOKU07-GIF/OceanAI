from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/map",
    tags=["Ocean Map"],
)


@router.get(
    "/status",
    summary="Ocean Map Status",
)
def map_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Ocean Map Health Check.

    This endpoint verifies that:

    - User Authentication works
    - Database connection works
    - Map module is available
    """

    return {
        "success": True,
        "message": "OceanAI Map Module is Ready",
        "data": {
            "user": current_user.username,
            "module": "Ocean Map",
            "version": "1.0.0",
            "status": "Online"
        }
    }
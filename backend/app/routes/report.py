from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.ocean_data import OceanData
from app.services.report_service import generate_report

router = APIRouter(
    prefix="/report",
    tags=["Reports"]
)


@router.get("/download")
def download_report(
    db: Session = Depends(get_db)
):

    records = db.query(OceanData).all()

    pdf = generate_report(records)

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=OceanAI_Report.pdf"
        }
    )
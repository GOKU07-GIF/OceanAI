from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.ocean_data import OceanData


def temperature_trend(db: Session):

    data = db.query(
        OceanData.location,
        OceanData.temperature
    ).all()

    return [
        {
            "location": row.location,
            "temperature": row.temperature
        }
        for row in data
    ]


def ph_trend(db: Session):

    data = db.query(
        OceanData.location,
        OceanData.ph
    ).all()

    return [
        {
            "location": row.location,
            "ph": row.ph
        }
        for row in data
    ]


def location_summary(db: Session):

    data = (
        db.query(
            OceanData.location,
            func.count(OceanData.id).label("count")
        )
        .group_by(OceanData.location)
        .all()
    )

    return [
        {
            "location": row.location,
            "records": row.count
        }
        for row in data
    ]
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.ocean_data import OceanData


def temperature_trend(db: Session):
    data = (
        db.query(OceanData)
        .order_by(OceanData.created_at.asc())
        .all()
    )

    return [
        {
            "latitude": row.latitude,
            "longitude": row.longitude,
            "temperature": row.temperature,
            "created_at": row.created_at,
        }
        for row in data
    ]


def ph_trend(db: Session):
    data = (
        db.query(OceanData)
        .order_by(OceanData.created_at.asc())
        .all()
    )

    return [
        {
            "latitude": row.latitude,
            "longitude": row.longitude,
            "ph": row.ph,
            "created_at": row.created_at,
        }
        for row in data
    ]


def location_summary(db: Session):
    data = (
        db.query(
            OceanData.latitude,
            OceanData.longitude,
            func.count(OceanData.id).label("count"),
        )
        .group_by(
            OceanData.latitude,
            OceanData.longitude,
        )
        .order_by(func.count(OceanData.id).desc())
        .all()
    )

    return [
        {
            "latitude": row.latitude,
            "longitude": row.longitude,
            "records": row.count,
        }
        for row in data
    ]

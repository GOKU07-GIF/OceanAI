from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.ocean_data import OceanData
from app.models.sensor_device import SensorDevice
from app.models.user import User


def get_dashboard_stats(db: Session):
    """
    Return live dashboard statistics from the database.

    Ocean metrics are calculated from OceanData records, while
    alert and sensor counts come from their respective tables.
    """

    total_records = db.query(OceanData).count()
    total_users = db.query(User).count()

    average_temperature = (
        db.query(func.avg(OceanData.temperature)).scalar() or 0
    )

    average_ph = (
        db.query(func.avg(OceanData.ph)).scalar() or 0
    )

    average_salinity = (
        db.query(func.avg(OceanData.salinity)).scalar() or 0
    )

    average_oxygen = (
        db.query(func.avg(OceanData.oxygen)).scalar() or 0
    )

    active_alerts = (
        db.query(Alert)
        .filter(Alert.is_read.is_(False))
        .count()
    )

    active_sensors = (
        db.query(SensorDevice)
        .filter(SensorDevice.is_active.is_(True))
        .count()
    )

    # Temporary water-quality score until the trained AI model
    # becomes the source of the dashboard risk calculation.
    water_quality = round(
        (
            average_ph * 10
            + average_oxygen * 10
            + average_salinity
        ) / 3,
        2,
    )

    ai_risk = "LOW"

    if water_quality < 60:
        ai_risk = "HIGH"
    elif water_quality < 80:
        ai_risk = "MEDIUM"

    return {
        "total_records": total_records,
        "total_users": total_users,
        "average_temperature": round(average_temperature, 2),
        "average_ph": round(average_ph, 2),
        "salinity": round(average_salinity, 2),
        "oxygen": round(average_oxygen, 2),
        "water_quality": water_quality,
        "active_alerts": active_alerts,
        "active_sensors": active_sensors,
        "ai_risk": ai_risk,
    }

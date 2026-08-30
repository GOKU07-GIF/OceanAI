from math import radians, sin, cos, sqrt, atan2

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.sos import SOS
from app.models.ocean_data import OceanData

from app.repositories.sos_repository import SOSRepository
from app.services.alert_service import AlertService


class SOSService:
    """
    Business logic for SOS requests.
    """

    # ============================================================
    # CALCULATE DISTANCE BETWEEN TWO GPS LOCATIONS
    # ============================================================

    @staticmethod
    def calculate_distance(
        latitude1: float,
        longitude1: float,
        latitude2: float,
        longitude2: float,
    ) -> float:

        earth_radius = 6371.0

        lat1 = radians(latitude1)
        lon1 = radians(longitude1)

        lat2 = radians(latitude2)
        lon2 = radians(longitude2)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            sin(dlat / 2) ** 2
            + cos(lat1)
            * cos(lat2)
            * sin(dlon / 2) ** 2
        )

        c = 2 * atan2(
            sqrt(a),
            sqrt(1 - a),
        )

        return earth_radius * c


    # ============================================================
    # FIND NEAREST ACTIVE STATION
    # ============================================================

    @staticmethod
    def find_nearest_active_station(
        db: Session,
        latitude: float,
        longitude: float,
    ):

        stations = (
            db.query(OceanData)
            .filter(
                OceanData.is_active.is_(True)
            )
            .all()
        )

        if not stations:
            return None

        nearest_station = None
        nearest_distance = float("inf")

        for station in stations:

            distance = SOSService.calculate_distance(
                latitude,
                longitude,
                station.latitude,
                station.longitude,
            )

            if distance < nearest_distance:
                nearest_distance = distance
                nearest_station = station

        return nearest_station


    # ============================================================
    # CREATE SOS
    # ============================================================

    @staticmethod
    def create_sos(
        db: Session,
        latitude: float,
        longitude: float,
        user_id: int,
    ):

        # Check whether the user already has an active SOS
        existing_sos = SOSRepository.get_active_by_user(
            db=db,
            user_id=user_id,
        )

        if existing_sos is not None:
            raise HTTPException(
                status_code=400,
                detail="You already have an active SOS request.",
            )

        # Find the nearest active ocean station
        nearest_station = (
            SOSService.find_nearest_active_station(
                db=db,
                latitude=latitude,
                longitude=longitude,
            )
        )

        # Create new SOS object
        sos = SOS(
            latitude=latitude,
            longitude=longitude,
            user_id=user_id,
            station_id=(
                nearest_station.id
                if nearest_station
                else None
            ),
            status="ACTIVE",
        )

        # Save SOS in database
        created_sos = SOSRepository.create(
            db,
            sos,
        )

        # Automatically create an emergency alert
        AlertService.create_alert(
            db=db,
            title="Emergency SOS Activated",
            message=(
                f"An emergency SOS request has been activated. "
                f"Location: {latitude:.6f}, {longitude:.6f}."
            ),
            alert_type="SOS",
            severity="CRITICAL",
            user_id=user_id,
            sos_id=created_sos.id,
        )

        return created_sos


    # ============================================================
    # GET ALL SOS
    # ============================================================

    @staticmethod
    def get_all_sos(
        db: Session,
    ):
        return SOSRepository.get_all(db)


    # ============================================================
    # GET SOS BY ID
    # ============================================================

    @staticmethod
    def get_sos_by_id(
        db: Session,
        sos_id: int,
    ):

        sos = SOSRepository.get_by_id(
            db,
            sos_id,
        )

        if sos is None:
            raise HTTPException(
                status_code=404,
                detail="SOS request not found",
            )

        return sos


    # ============================================================
    # UPDATE SOS STATUS
    # ============================================================

    @staticmethod
    def update_sos_status(
        db: Session,
        sos_id: int,
        status: str,
    ):

        sos = SOSRepository.get_by_id(
            db,
            sos_id,
        )

        if sos is None:
            raise HTTPException(
                status_code=404,
                detail="SOS request not found",
            )

        allowed_statuses = {
            "ACTIVE",
            "RESOLVED",
            "CANCELLED",
        }

        if status not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid SOS status. "
                    "Use ACTIVE, RESOLVED, or CANCELLED."
                ),
            )

        sos.status = status

        return SOSRepository.update(
            db,
            sos,
        )
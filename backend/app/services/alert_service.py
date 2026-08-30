from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.repositories.alert_repository import AlertRepository


class AlertService:
    """
    Business logic for alerts.
    """

    # ============================================================
    # CREATE ALERT
    # ============================================================

    @staticmethod
    def create_alert(
        db: Session,
        title: str,
        message: str,
        alert_type: str,
        severity: str,
        user_id: int | None = None,
        sos_id: int | None = None,
    ):

        allowed_severities = {
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
        }

        if severity not in allowed_severities:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid severity. "
                    "Use LOW, MEDIUM, HIGH, or CRITICAL."
                ),
            )

        alert = Alert(
            title=title,
            message=message,
            alert_type=alert_type,
            severity=severity,
            user_id=user_id,
            sos_id=sos_id,
            is_read=False,
        )

        return AlertRepository.create(
            db,
            alert,
        )


    # ============================================================
    # GET ALL ALERTS
    # ============================================================

    @staticmethod
    def get_all_alerts(
        db: Session,
    ):
        return AlertRepository.get_all(db)


    # ============================================================
    # GET ALERT BY ID
    # ============================================================

    @staticmethod
    def get_alert_by_id(
        db: Session,
        alert_id: int,
    ):
        alert = AlertRepository.get_by_id(
            db,
            alert_id,
        )

        if alert is None:
            raise HTTPException(
                status_code=404,
                detail="Alert not found",
            )

        return alert


    # ============================================================
    # GET ALERTS FOR A USER
    # ============================================================

    @staticmethod
    def get_user_alerts(
        db: Session,
        user_id: int,
    ):
        return AlertRepository.get_by_user(
            db,
            user_id,
        )


    # ============================================================
    # GET UNREAD ALERTS FOR A USER
    # ============================================================

    @staticmethod
    def get_unread_user_alerts(
        db: Session,
        user_id: int,
    ):
        return AlertRepository.get_unread_by_user(
            db,
            user_id,
        )


    # ============================================================
    # MARK ONE ALERT AS READ
    # ============================================================

    @staticmethod
    def mark_alert_as_read(
        db: Session,
        alert_id: int,
    ):
        alert = AlertRepository.get_by_id(
            db,
            alert_id,
        )

        if alert is None:
            raise HTTPException(
                status_code=404,
                detail="Alert not found",
            )

        return AlertRepository.mark_as_read(
            db,
            alert,
        )


    # ============================================================
    # MARK ALL USER ALERTS AS READ
    # ============================================================

    @staticmethod
    def mark_all_user_alerts_as_read(
        db: Session,
        user_id: int,
    ):
        AlertRepository.mark_all_as_read(
            db,
            user_id,
        )

        return {
            "message": "All alerts marked as read"
        }
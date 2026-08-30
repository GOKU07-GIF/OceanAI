from sqlalchemy.orm import Session, joinedload

from app.models.alert import Alert


class AlertRepository:
    """
    Database operations for alerts.
    """

    # ============================================================
    # CREATE ALERT
    # ============================================================

    @staticmethod
    def create(
        db: Session,
        alert: Alert,
    ):
        db.add(alert)

        db.commit()

        db.refresh(alert)

        return alert


    # ============================================================
    # GET ALL ALERTS
    # ============================================================

    @staticmethod
    def get_all(
        db: Session,
    ):
        return (
            db.query(Alert)
            .order_by(
                Alert.created_at.desc()
            )
            .all()
        )


    # ============================================================
    # GET ALERT BY ID
    # ============================================================

    @staticmethod
    def get_by_id(
        db: Session,
        alert_id: int,
    ):
        return (
            db.query(Alert)
            .filter(
                Alert.id == alert_id
            )
            .first()
        )


    # ============================================================
    # GET ALERTS BY USER
    # ============================================================

    @staticmethod
    def get_by_user(
        db: Session,
        user_id: int,
    ):
        return (
            db.query(Alert)
            .filter(
                Alert.user_id == user_id
            )
            .order_by(
                Alert.created_at.desc()
            )
            .all()
        )


    # ============================================================
    # GET UNREAD ALERTS BY USER
    # ============================================================

    @staticmethod
    def get_unread_by_user(
        db: Session,
        user_id: int,
    ):
        return (
            db.query(Alert)
            .filter(
                Alert.user_id == user_id,
                Alert.is_read.is_(False),
            )
            .order_by(
                Alert.created_at.desc()
            )
            .all()
        )


    # ============================================================
    # MARK ALERT AS READ
    # ============================================================

    @staticmethod
    def mark_as_read(
        db: Session,
        alert: Alert,
    ):
        alert.is_read = True

        db.commit()

        db.refresh(alert)

        return alert


    # ============================================================
    # MARK ALL USER ALERTS AS READ
    # ============================================================

    @staticmethod
    def mark_all_as_read(
        db: Session,
        user_id: int,
    ):
        (
            db.query(Alert)
            .filter(
                Alert.user_id == user_id,
                Alert.is_read.is_(False),
            )
            .update(
                {
                    Alert.is_read: True
                },
                synchronize_session=False,
            )
        )

        db.commit()
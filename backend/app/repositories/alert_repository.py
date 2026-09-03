from sqlalchemy.orm import Session

from app.models.alert import Alert


class AlertRepository:
    """
    Database operations for alerts.
    """

    @staticmethod
    def create(
        db: Session,
        alert: Alert,
        commit: bool = False,
    ):
        db.add(alert)

        if commit:
            db.commit()
            db.refresh(alert)

        return alert

    @staticmethod
    def get_all(db: Session):
        return (
            db.query(Alert)
            .order_by(Alert.created_at.desc())
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, alert_id: int):
        return (
            db.query(Alert)
            .filter(Alert.id == alert_id)
            .first()
        )

    @staticmethod
    def get_by_user(db: Session, user_id: int):
        return (
            db.query(Alert)
            .filter(Alert.user_id == user_id)
            .order_by(Alert.created_at.desc())
            .all()
        )

    @staticmethod
    def get_unread_by_user(db: Session, user_id: int):
        return (
            db.query(Alert)
            .filter(
                Alert.user_id == user_id,
                Alert.is_read.is_(False),
            )
            .order_by(Alert.created_at.desc())
            .all()
        )

    @staticmethod
    def mark_as_read(db: Session, alert: Alert):
        alert.is_read = True
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int):
        (
            db.query(Alert)
            .filter(
                Alert.user_id == user_id,
                Alert.is_read.is_(False),
            )
            .update(
                {Alert.is_read: True},
                synchronize_session=False,
            )
        )
        db.commit()

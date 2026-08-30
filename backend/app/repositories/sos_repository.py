from sqlalchemy.orm import Session, joinedload

from app.models.sos import SOS


class SOSRepository:
    """
    Database operations for SOS requests.
    """

    # ============================================================
    # CHECK ACTIVE SOS FOR USER
    # ============================================================

    @staticmethod
    def get_active_by_user(
        db: Session,
        user_id: int,
    ):
        return (
            db.query(SOS)
            .filter(
                SOS.user_id == user_id,
                SOS.status == "ACTIVE",
            )
            .first()
        )


    # ============================================================
    # CREATE SOS
    # ============================================================

    @staticmethod
    def create(
        db: Session,
        sos: SOS,
    ):
        db.add(sos)
        db.commit()
        db.refresh(sos)

        return sos


    # ============================================================
    # GET ALL SOS
    # ============================================================

    @staticmethod
    def get_all(
        db: Session,
    ):
        return (
            db.query(SOS)
            .options(
                joinedload(SOS.station)
            )
            .order_by(
                SOS.created_at.desc()
            )
            .all()
        )


    # ============================================================
    # GET SOS BY ID
    # ============================================================

    @staticmethod
    def get_by_id(
        db: Session,
        sos_id: int,
    ):
        return (
            db.query(SOS)
            .options(
                joinedload(SOS.station)
            )
            .filter(
                SOS.id == sos_id
            )
            .first()
        )


    # ============================================================
    # UPDATE SOS
    # ============================================================

    @staticmethod
    def update(
        db: Session,
        sos: SOS,
    ):
        db.commit()
        db.refresh(sos)

        return sos
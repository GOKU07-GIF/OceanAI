from sqlalchemy.orm import Session

from app.models.ocean_data import OceanData


class OceanRepository:
    """
    Repository for Ocean Data CRUD operations.
    """

    @staticmethod
    def create(
        db: Session,
        ocean_data: OceanData,
    ) -> OceanData:
        db.add(ocean_data)
        db.commit()
        db.refresh(ocean_data)
        return ocean_data

    @staticmethod
    def get_all(
        db: Session,
    ):
        return (
            db.query(OceanData)
            .order_by(OceanData.id.desc())
            .all()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        ocean_id: int,
    ):
        return (
            db.query(OceanData)
            .filter(OceanData.id == ocean_id)
            .first()
        )

    @staticmethod
    def update(
        db: Session,
        ocean_data: OceanData,
    ):
        db.commit()
        db.refresh(ocean_data)
        return ocean_data

    @staticmethod
    def delete(
        db: Session,
        ocean_data: OceanData,
    ):
        db.delete(ocean_data)
        db.commit()
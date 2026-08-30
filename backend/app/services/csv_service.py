import pandas as pd
from sqlalchemy.orm import Session

from app.models.ocean_data import OceanData


def import_csv(db: Session, file):

    df = pd.read_csv(file.file)

    records = []

    for _, row in df.iterrows():

        ocean = OceanData(
            location=row["location"],
            temperature=row["temperature"],
            ph=row["ph"],
            owner_id=row["owner_id"]
        )

        records.append(ocean)

    db.add_all(records)
    db.commit()

    return {
        "message": "CSV Imported Successfully",
        "total_records": len(records)
    }
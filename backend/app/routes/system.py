from fastapi import APIRouter
from app.database.database import engine

router = APIRouter(
    prefix="/system",
    tags=["System"],
)

@router.get("/database")
def database_status():
    try:
        connection = engine.connect()
        connection.close()

        return {
            "status": "Database Connected Successfully"
        }

    except Exception as e:
        return {
            "status": "Failed",
            "error": str(e)
        }
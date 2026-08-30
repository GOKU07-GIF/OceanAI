from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):

    total_records: int

    total_users: int

    average_temperature: float

    average_ph: float

    water_quality: float

    salinity: float

    dissolved_oxygen: float

    active_alerts: int

    active_sensors: int

    ai_risk: str
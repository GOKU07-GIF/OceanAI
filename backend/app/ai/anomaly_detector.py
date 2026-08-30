def detect_anomaly(
    temperature: float,
    ph: float,
    salinity: float,
    dissolved_oxygen: float
):

    alerts = []

    if temperature > 35:
        alerts.append("High Temperature")

    if temperature < 10:
        alerts.append("Very Low Temperature")

    if ph < 6.5 or ph > 8.5:
        alerts.append("Unsafe pH")

    if salinity > 37:
        alerts.append("High Salinity")

    if dissolved_oxygen < 5:
        alerts.append("Low Dissolved Oxygen")

    if alerts:
        return {
            "status": "Alert",
            "alerts": alerts
        }

    return {
        "status": "Normal",
        "alerts": []
    }
class SeaHealthAnalyzer:
    """
    AI Engine for Ocean Health Analysis.
    """

    @staticmethod
    def analyze(
        temperature: float,
        ph: float,
        salinity: float,
        oxygen: float,
    ) -> dict:

        score = 100
        recommendations = []

        # -----------------------------
        # Temperature
        # -----------------------------
        if 20 <= temperature <= 30:
            recommendations.append(
                "Water temperature is healthy."
            )
        else:
            score -= 20
            recommendations.append(
                "Abnormal water temperature detected."
            )

        # -----------------------------
        # pH
        # -----------------------------
        if 7.8 <= ph <= 8.4:
            recommendations.append(
                "pH level is ideal."
            )
        else:
            score -= 25
            recommendations.append(
                "pH is outside the safe range."
            )

        # -----------------------------
        # Salinity
        # -----------------------------
        if 30 <= salinity <= 37:
            recommendations.append(
                "Salinity level is normal."
            )
        else:
            score -= 25
            recommendations.append(
                "Abnormal salinity detected."
            )

        # -----------------------------
        # Dissolved Oxygen
        # -----------------------------
        if oxygen >= 5:
            recommendations.append(
                "Dissolved oxygen is sufficient."
            )
        else:
            score -= 30
            recommendations.append(
                "Low dissolved oxygen detected."
            )

        # -----------------------------
        # Risk Level
        # -----------------------------
        if score >= 90:
            risk = "Low"
            quality = "Excellent"

        elif score >= 70:
            risk = "Moderate"
            quality = "Good"

        elif score >= 50:
            risk = "High"
            quality = "Poor"

        else:
            risk = "Critical"
            quality = "Dangerous"

        return {
            "sea_health_score": score,
            "risk_level": risk,
            "water_quality": quality,
            "recommendations": recommendations,
        }
def get_recommendation(
    wind_speed,
    power_density,
    site_score
):

    if site_score < 40:

        verdict = "Poor"

        application = (
            "Not recommended for wind projects"
        )

    elif site_score < 55:

        verdict = "Marginal"

        application = (
            "Small wind turbine or hybrid solar-wind"
        )

    elif site_score < 70:

        verdict = "Moderate"

        application = (
            "Community scale wind project"
        )

    elif site_score < 85:

        verdict = "Good"

        application = (
            "Commercial wind farm"
        )

    else:

        verdict = "Excellent"

        application = (
            "Utility scale wind development"
        )

    return verdict, application
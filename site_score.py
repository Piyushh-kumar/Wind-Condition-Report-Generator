def calculate_site_score(
    wind_speed,
    power_density
):

    wind_component = min(
        wind_speed / 8,
        1
    ) * 70

    power_component = min(
        power_density / 500,
        1
    ) * 30

    return round(
        wind_component +
        power_component
    )
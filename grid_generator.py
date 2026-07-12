import math


def generate_grid(
    lat,
    lon,
    radius_km
):

    if radius_km <= 0.2:
        step_km = 0.025      # 25 m

    elif radius_km <= 0.5:
        step_km = 0.05       # 50 m

    elif radius_km <= 1:
        step_km = 0.1        # 100 m

    else:
        step_km = 0.25       # 250 m

    points = []

    lat_step = step_km / 111

    lon_step = step_km / (
        111 * abs(
            math.cos(
                math.radians(lat)
            )
        )
    )

    num_steps = max(
        1,
        int(radius_km / step_km)
    )

    for i in range(
        -num_steps,
        num_steps + 1
    ):

        for j in range(
            -num_steps,
            num_steps + 1
        ):

            new_lat = (
                lat +
                i * lat_step
            )

            new_lon = (
                lon +
                j * lon_step
            )

            points.append(
                (
                    new_lat,
                    new_lon
                )
            )

    return points
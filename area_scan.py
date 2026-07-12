from grid_generator import generate_grid
from site_scan import scan_wind_only


def scan_area(
    lat,
    lon,
    hub_height,
    radius_km
):

    points = generate_grid(
        lat,
        lon,
        radius_km
    )

    print(
        "Generated points:",
        len(points)
    )

    results = []

    for point_lat, point_lon in points:

        try:

            wind = scan_wind_only(
                point_lat,
                point_lon,
                hub_height
            )

            results.append(
                {
                    "lat": point_lat,
                    "lon": point_lon,
                    "wind": wind
                }
            )

        except Exception as e:

            print(
                f"Error at {point_lat}, {point_lon}: {e}"
            )

    print(
        "Valid results:",
        len(results)
    )

    return results
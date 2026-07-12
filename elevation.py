import requests


def get_elevation(
    lat,
    lon
):

    try:

        url = (
            "https://api.open-meteo.com/v1/elevation"
            f"?latitude={lat}"
            f"&longitude={lon}"
        )

        response = requests.get(
            url,
            timeout=20
        )

        if response.status_code != 200:
            return 0

        data = response.json()

        if (
            "elevation" not in data
            or
            len(data["elevation"]) == 0
        ):
            return 0

        return float(
            data["elevation"][0]
        )

    except Exception:

        return 0
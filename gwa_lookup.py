import rasterio

# WIND SPEED FILES

ds10 = rasterio.open(
    "IND_wind-speed_10m.tif"
)

ds50 = rasterio.open(
    "IND_wind-speed_50m.tif"
)

ds100 = rasterio.open(
    "IND_wind-speed_100m.tif"
)

ds150 = rasterio.open(
    "IND_wind-speed_150m.tif"
)

ds200 = rasterio.open(
    "IND_wind-speed_200m.tif"
)


def get_value(
    dataset,
    lat,
    lon
):

    try:

        for value in dataset.sample(
            [(lon, lat)]
        ):

            return float(
                value[0]
            )

    except Exception:

        return 0.0


def get_all_wind_speeds(
    lat,
    lon
):

    return {

        "10m": get_value(
            ds10,
            lat,
            lon
        ),

        "50m": get_value(
            ds50,
            lat,
            lon
        ),

        "100m": get_value(
            ds100,
            lat,
            lon
        ),

        "150m": get_value(
            ds150,
            lat,
            lon
        ),

        "200m": get_value(
            ds200,
            lat,
            lon
        )

    }
import rasterio

pd10 = rasterio.open(
    "IND_power-density_10m.tif"
)

pd50 = rasterio.open(
    "IND_power-density_50m.tif"
)

pd100 = rasterio.open(
    "IND_power-density_100m.tif"
)

pd150 = rasterio.open(
    "IND_power-density_150m.tif"
)

pd200 = rasterio.open(
    "IND_power-density_200m.tif"
)


def get_value(dataset, lat, lon):

    for val in dataset.sample(
        [(lon, lat)]
    ):
        return float(val[0])


def get_all_power_densities(
    lat,
    lon
):

    return {
        "10m": get_value(
            pd10,
            lat,
            lon
        ),

        "50m": get_value(
            pd50,
            lat,
            lon
        ),

        "100m": get_value(
            pd100,
            lat,
            lon
        ),

        "150m": get_value(
            pd150,
            lat,
            lon
        ),

        "200m": get_value(
            pd200,
            lat,
            lon
        )
    }
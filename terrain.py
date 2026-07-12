import rasterio
import numpy as np

# Safe global initialization to prevent startup crashes
try:
    dem = rasterio.open("IND_DEM.tif")
except Exception:
    dem = None


def get_elevation(lat, lon):
    if dem is None:
        return 0.0
    try:
        for value in dem.sample([(lon, lat)]):
            return float(value[0])
    except Exception:
        return 0.0


def get_slope(lat, lon):
    if dem is None:
        return 0.0

    try:
        row, col = dem.index(lon, lat)

        window = rasterio.windows.Window(
            col_off=max(col - 1, 0),
            row_off=max(row - 1, 0),
            width=3,
            height=3
        )

        data = dem.read(
            1,
            window=window
        )

        transform = dem.window_transform(window)

        xres = transform.a
        yres = abs(transform.e)

        dz_dy, dz_dx = np.gradient(
            data,
            yres,
            xres
        )

        slope = np.degrees(
            np.arctan(
                np.sqrt(
                    dz_dx**2 +
                    dz_dy**2
                )
            )
        )

        return float(slope[1, 1])
    except Exception:
        return 0.0


def get_terrain_rating(slope):
    if dem is None:
        return "Data Missing (Cleared)"
        
    if slope < 5:
        return "Excellent"
    elif slope < 10:
        return "Good"
    elif slope < 20:
        return "Moderate"
    else:
        return "Poor"
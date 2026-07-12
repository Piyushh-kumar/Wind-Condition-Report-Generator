import rasterio

files = [
    "IND_wind-speed_50m.tif",
    "IND_wind-speed_100m.tif",
    "IND_wind-speed_150m.tif",
    "IND_wind-speed_200m.tif"
]

for f in files:
    try:
        ds = rasterio.open(f)
        print(f"{f}  OK")
        print(ds.width, ds.height)

    except Exception as e:
        print(f"{f}  FAILED")
        print(e)
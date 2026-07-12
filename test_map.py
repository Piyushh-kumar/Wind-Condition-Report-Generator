import folium

from area_scan import scan_area
from map_visualization import add_wind_points


lat = 18.5204
lon = 73.8567
hub_height = 100
radius_km = 1
results = scan_area(
    lat,
    lon,
    hub_height,
    radius_km
)

m = folium.Map(
    location=[
        lat,
        lon,
    ],
    zoom_start=12
)

m = add_wind_points(
    m,
    results
)

m.save(
    "wind_map.html"
)

print(
    "Map Saved"
)
print(
    min(
        r["wind"]
        for r in results
    )
)

print(
    max(
        r["wind"]
        for r in results
    )
)
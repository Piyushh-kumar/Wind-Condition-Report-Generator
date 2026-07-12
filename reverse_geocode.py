from geopy.geocoders import Nominatim

geolocator = Nominatim(
    user_agent="wind_ai",
    timeout=10
)

def get_address(lat, lon):
    try:
        location = geolocator.reverse((lat, lon))
        if location:
            return location.address
        return "Unknown Location"
    except Exception:
        return "Unknown Location"
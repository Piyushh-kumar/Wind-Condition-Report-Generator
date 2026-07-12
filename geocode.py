from geopy.geocoders import Nominatim

geolocator = Nominatim(
    user_agent="wind_ai"
)

def search_location(place):

    location = geolocator.geocode(
        place
    )

    if location:

        return (
            location.latitude,
            location.longitude
        )

    return None
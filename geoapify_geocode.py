import requests
import streamlit as st

API_KEY = st.secrets["GEOAPIFY_API_KEY"]

def get_coordinates(place):
    url = "https://api.geoapify.com/v1/geocode/search"
    try:
        response = requests.get(
            url,
            params={
                "text": place,
                "limit": 1,
                "apiKey": API_KEY
            },
            timeout=10
        )
        data = response.json()
        features = data.get("features", [])

        if not features:
            return None

        lon, lat = features[0]["geometry"]["coordinates"]
        return lat, lon
    except Exception:
        return None
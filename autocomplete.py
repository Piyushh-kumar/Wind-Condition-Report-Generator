import requests
import streamlit as st

API_KEY = st.secrets["GEOAPIFY_API_KEY"]

def get_suggestions(text):
    url = "https://api.geoapify.com/v1/geocode/autocomplete"
    try:
        response = requests.get(
            url,
            params={
                "text": text,
                "limit": 5,
                "apiKey": API_KEY
            },
            timeout=10
        )
        data = response.json()
        
        suggestions = []
        for feature in data.get("features", []):
            prop = feature.get("properties", {})
            # Read the most detailed formatted string address string available
            formatted_address = prop.get("formatted", "")
            if formatted_address and formatted_address not in suggestions:
                suggestions.append(formatted_address)
                
        return suggestions
    except Exception:
        return []
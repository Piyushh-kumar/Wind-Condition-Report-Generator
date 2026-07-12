import requests

API_KEY = "YOUR_KEY"

def autocomplete(
    query
):

    url = (
        "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    )

    response = requests.get(
        url,
        params={
            "input": query,
            "key": API_KEY
        }
    )

    data = response.json()

    return [
        item["description"]
        for item in data["predictions"]
    ]
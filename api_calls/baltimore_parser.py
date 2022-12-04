import requests


def baltimore_crime():
    # need to figure out what time period this covers
    # Start of 2021: 1609459200000
    # End of 2022:   1672531199000
    queryURL = "https://opendata.baltimorecity.gov/egis/rest/services/NonSpatialTables/Part1_Crime/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json"
    queryURL = "https://opendata.baltimorecity.gov/egis/rest/services/NonSpatialTables/Part1_Crime/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json"

    response = requests.get(queryURL)
    data = response.json()
    print(data)

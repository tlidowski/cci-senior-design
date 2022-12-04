import requests


def dc_crime_2022():
    queryURL= "https://maps2.dcgis.dc.gov/dcgis/rest/services/FEEDS/MPD/MapServer/4/query?where=1%3D1&outFields=*&outSR=4326&f=json"
    response = requests.get(queryURL)
    data = response.json()
    print(data)

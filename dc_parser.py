import requests
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import csv
from bs4 import BeautifulSoup
import io


def dc_crime_2022():
    queryURL= "https://maps2.dcgis.dc.gov/dcgis/rest/services/FEEDS/MPD/MapServer/4/query?where=1%3D1&outFields=*&outSR=4326&f=json"
    response = requests.get(queryURL)
    data = response.json()
    print(data)

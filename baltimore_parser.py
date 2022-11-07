import requests
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import csv
from bs4 import BeautifulSoup
import io

def baltimore_crime():
    #need to figure out what time period this covers
    queryURL= "https://opendata.baltimorecity.gov/egis/rest/services/NonSpatialTables/Part1_Crime/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json"
    response = requests.get(queryURL)
    data = response.json()
    print(data)
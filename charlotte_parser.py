import requests
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import csv
from bs4 import BeautifulSoup
import io

#need to figure out what this was: https://gis.charlottenc.gov/arcgis/rest/services/ODP/ViolentCrimeData/MapServer/4/query?where=1%3D1&outFields=*&outSR=4326&f=json

#https://data.charlottenc.gov/datasets/charlotte::cmpd-incidents-1/api
def charlotte_incident_reports():
    #need to figure out what time period this covers
    queryURL= "https://gis.charlottenc.gov/arcgis/rest/services/CMPD/CMPDIncidents/MapServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json"
    response = requests.get(queryURL)
    data = response.json()
    print(data)


#https://data.charlottenc.gov/datasets/charlotte::cmpd-violent-crime/api
def charlotte_violent_crime():
    queryURL = "https://gis.charlottenc.gov/arcgis/rest/services/ODP/ViolentCrimeData/MapServer/4/query?where=1%3D1&outFields=*&outSR=4326&f=json"
    response = requests.get(queryURL)
    data = response.json()
    print(data)

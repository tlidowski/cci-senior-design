import requests
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import csv
from bs4 import BeautifulSoup
import io

def national_crime_estimate_to_from_year(start, end, key):
    base = 'https://api.usa.gov/crime/fbi/sapi/api'
    crime_last_year = '/estimates/national/' + str(start) + '/' + str(end)
    response = requests.get(base + crime_last_year + "?API_KEY=" + key)
    data = response.json()
    print(data)


def state_crime_estimate_to_from_year(state_abbrev, start, end, key):
    base = 'https://api.usa.gov/crime/fbi/sapi/api'
    summary_by_state_year = '/estimates/states/' + state_abbrev + "/" + str(start) + '/' + str(end)
    response = requests.get(base + summary_by_state_year + "?API_KEY=" + key)
    data = response.json()
    print(data)

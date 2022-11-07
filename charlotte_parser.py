import requests
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import csv
from bs4 import BeautifulSoup
import io

https://gis.charlottenc.gov/arcgis/rest/services/ODP/ViolentCrimeData/MapServer/4/query?where=1%3D1&outFields=*&outSR=4326&f=json
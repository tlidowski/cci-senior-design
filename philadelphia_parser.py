import requests
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import csv
from bs4 import BeautifulSoup
import io


def format_table_view():
    pd.set_option('display.max_columns', None)


def philadelphia_data_by_year(year):
    philadelphia_crime_data_website = requests.get('https://www.opendataphilly.org/dataset/crime-incidents')
    soup = BeautifulSoup(philadelphia_crime_data_website.content, 
'html.parser')
    csv_list = soup.find('section', 
id='dataset-resources').find('ul').find_all(True, recursive=False)
    for csv_element in csv_list:
        csv_element_children = csv_element.find_all(True, recursive=False)
        csv_name = csv_element_children[0].text.split('(')[0]
        csv_link = \
            csv_element_children[2].find_all(True, 
recursive=False)[1].find_all(True, recursive=False)[1].find('a')[
                'href']
        if year in csv_name:
            with requests.Session() as session:
                download = session.get(csv_link)
                decoded_content = download.content.decode('utf-8')
                table = pd.read_csv(io.StringIO(decoded_content))
                print(table.head())
            break

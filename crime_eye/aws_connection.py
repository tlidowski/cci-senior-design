import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import datetime

def format_table_view():
    pd.set_option('display.max_columns', None)


def connectAWS():
    engine = psycopg2.connect(
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USERNAME"),
        password=input("Enter Password Please: "),
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
    )
    return engine


def executeGetQuery(query, engine):
    return pd.read_sql(query, con=engine)


def getCityData(cityName, engine):
    query = 'select * from all_crime where city_name=' + "'" + cityName + "'"
    return pd.read_sql(query, con=engine)

def getCityDataGivenYears(cityName, start, end, engine):
    start = f"'{start}0101'"
    end = f"'{end}1231'"
    query = 'select * from all_crime where city_name=' + "'" + cityName + "'" + f' AND date >= {start} and date<= {end}'
    print(query)
    return pd.read_sql(query, con=engine)

def get_crime_descriptions(cityName, engine):
    descr_query = "select distinct crime_description from all_crime where city_name = '" + cityName + "'"
    description = executeGetQuery(descr_query, engine)['crime_description'].tolist()
    return description

def initConnection():
    format_table_view()
    load_dotenv()
    currentEngine = connectAWS()
    return currentEngine
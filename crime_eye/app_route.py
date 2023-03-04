import json

import numpy as np
from flask import Flask, render_template, jsonify, request
import requests
import pandas as pd
from math import radians, cos, sin, asin, sqrt
import validation as v
import aws_connection as aws
app = Flask(__name__)
engine = None


def apply_mask(df, column_name, value):
    mask = (df[column_name] == value)
    # apply mask to result
    res = df[mask]
    return res


def get_column_types():
    column_types = {
        'CITY_NAME': 'object',
        'STATE_NAME': 'object',
        'CRIME_CODE': 'object',
        'CRIME_DESCRIPTION': 'object',
        'DATE_REPORTED': 'object',
        'DATE_OCCURRED': 'object',
        'LATITUDE': 'float64',
        'LONGITUDE': 'float64',
        'DATE_FORMAT': 'object'
    }
    return column_types

def get_lat_lon(df):
    lats = df['LATITUDE']
    lons = df["LONGITUDE"]
    return lats.tolist(), lons.tolist()

# https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 3956 # Radius of earth in Miles. Use 3956 for miles.
    return c * r

def get_location_from_name(city):
    # Lon, Lat
    nameMap = {
        "boston": [-71.0589, 42.3601,],
    }
    try:
        return nameMap[city.lower()]
    except:
        return [None, None]
    


# Only works if server is run in the crimeeye folder: python3
@app.route('/city_crime_data', methods=['GET'])
def get_city_crime_data():
    city = request.args.get('city')
    start = request.args.get('start')
    end = request.args.get('end')

    try:
        output = None
        path_2020 = f'../combined_city_data/city_data-{2020}.csv'
        path_2021 = f'../combined_city_data/city_data-{2021}.csv'

        year_csvs = {"2020": path_2020,
                     "2021": path_2021
                     }

        column_types = get_column_types()

        if (start in year_csvs.keys()) and (end in year_csvs.keys()):
            start_year_df = pd.read_csv(year_csvs[start], dtype=column_types)
            start_year_res = apply_mask(start_year_df, 'CITY_NAME', city)
            start_lats, start_lons = get_lat_lon(start_year_res)
            end_year_df = []
            end_year_res = []

            if start != end:
                end_year_df = pd.read_csv(year_csvs[end], dtype=column_types)
                end_year_res = apply_mask(end_year_df, 'CITY_NAME', city)
                end_lats, end_lons = get_lat_lon(start_year_res)



            # res = None
            if len(end_year_res) != 0:
                res = pd.concat([start_year_res, end_year_res], axis=0)
                lats = start_lats + end_lats
                lons = start_lons + end_lons

            else:
                res = start_year_res
                lats = start_lats
                lons = start_lons

            
        return res.to_json(orient='records')
    except Exception as e:
        print(e)
        return {}


@app.route('/city_geo_json', methods=['GET'])
def get_city_geo_data():
    city = request.args.get('city')
    start = request.args.get('start')
    end = request.args.get('end')
    geo_json = {"type": "FeatureCollection", "features": []}
    try:
        path_2020 = f'../combined_city_data/city_data-{2020}.csv'
        path_2021 = f'../combined_city_data/city_data-{2021}.csv'

        year_csvs = {"2020": path_2020,
                     "2021": path_2021
                     }

        column_types = get_column_types()

        if (start in year_csvs.keys()) and (end in year_csvs.keys()):
            start_year_df = pd.read_csv(year_csvs[start], dtype=column_types)
            start_year_res = apply_mask(start_year_df, 'CITY_NAME', city)

            end_year_df = []
            end_year_res = []

            if start != end:
                end_year_df = pd.read_csv(year_csvs[end], dtype=column_types)
                end_year_res = apply_mask(end_year_df, 'CITY_NAME', city)

            # res = None
            if len(end_year_res) != 0:
                res = pd.concat([start_year_res, end_year_res], axis=0)
            else:
                res = start_year_res
            for i, row in res.iterrows():
                if not (np.isnan(row["LONGITUDE"]) and np.isnan(row["LATITUDE"])):
                    template = {"type": "Feature", "geometry": {"type": "Point"}}
                    template["geometry"]["coordinates"] = [row["LONGITUDE"], row["LATITUDE"]]
                    geo_json["features"].append(template)
        return json.dumps(geo_json)
    except:
        print("Failure")
        return {}

@app.route('/crimes_in_radius', methods=['GET'])
def get_locations_given_radius():
    city = request.args.get('city')
    start = request.args.get('start')
    end = request.args.get('end')
    radius = int(request.args.get('radius'))
    try:
        path_2020 = f'../combined_city_data/city_data-{2020}.csv'
        path_2021 = f'../combined_city_data/city_data-{2021}.csv'

        year_csvs = {"2020": path_2020,
                     "2021": path_2021
                     }

        column_types = get_column_types()

        if (start in year_csvs.keys()) and (end in year_csvs.keys()):
            start_year_df = pd.read_csv(year_csvs[start], dtype=column_types)
            start_year_res = apply_mask(start_year_df, 'CITY_NAME', city)

            end_year_df = []
            end_year_res = []

            if start != end:
                end_year_df = pd.read_csv(year_csvs[end], dtype=column_types)
                end_year_res = apply_mask(end_year_df, 'CITY_NAME', city)

            # res = None
            if len(end_year_res) != 0:
                res = pd.concat([start_year_res, end_year_res], axis=0)
            else:
                res = start_year_res
            cityLocation = get_location_from_name(city)
            coords = {
                "inside": [],
                "outside": []
            }
            for i, row in res.iterrows():
                if not (np.isnan(row["LONGITUDE"]) and np.isnan(row["LATITUDE"])):
                    # return 2 separate lists of latitudes and longitudes based off whether they are within the radius
                    lat = row["LATITUDE"]
                    lon = row["LONGITUDE"]
                    if haversine(cityLocation[0], cityLocation[1], lon, lat) <= radius:
                        coords["inside"].append((lon, lat))
                    else:
                        coords["outside"].append((lon, lat))
        return json.dumps({
            "center": cityLocation,
            "coords":coords
        })
    except Exception as e:
        print(f'Faliure: {e}')
        return {}
    
@app.route('/crimes_pie_chart', methods=['GET'])
def get_pie_chart():
    city = request.args.get('city')
    start = request.args.get('start')
    end = request.args.get('end')
    try:
        path_2020 = f'../combined_city_data/city_data-{2020}.csv'
        path_2021 = f'../combined_city_data/city_data-{2021}.csv'

        year_csvs = {"2020": path_2020,
                     "2021": path_2021
                     }

        column_types = get_column_types()

        if (start in year_csvs.keys()) and (end in year_csvs.keys()):
            start_year_df = pd.read_csv(year_csvs[start], dtype=column_types)
            start_year_res = apply_mask(start_year_df, 'CITY_NAME', city)

            end_year_df = []
            end_year_res = []

            if start != end:
                end_year_df = pd.read_csv(year_csvs[end], dtype=column_types)
                end_year_res = apply_mask(end_year_df, 'CITY_NAME', city)

            # res = None
            if len(end_year_res) != 0:
                res = pd.concat([start_year_res, end_year_res], axis=0)
            else:
                res = start_year_res
        
            crimes_counted = res['CRIME_DESCRIPTION'].value_counts().rename_axis('crimes').reset_index(name='counts')
            counts_filtered = crimes_counted[crimes_counted['counts'] >= 1400]

        print(counts_filtered['counts'])
        return json.dumps({
            "counts": counts_filtered['counts'].to_list(),
            "crimes": counts_filtered['crimes'].to_list()
        })
    except Exception as e:
        print(f'Faliure: {e}')
        return {}
    
# Using AWS
@app.route('/crimes_from_address', methods=['GET'])
def get_locations_given_address():
    cityName = request.args.get('cityName')
    start = request.args.get('start')
    end = request.args.get('end')
    radius = int(request.args.get('radius'))
    userLat = float(request.args.get('lat'))
    userLon = float(request.args.get('lon'))


    # if engine == None:
    #     print("SERVER ERROR")

    if not v.validateYears(start, end):
        return json.dumps(
            {"errors":["Invalid Years"]}
        )
    if not v.validateCity(cityName):
        return json.dumps(
            {"errors":["No crime data for given city"]}
        )
    engine = aws.initConnection()
    res = aws.getCityData(cityName, engine)
    engine.close()
    print(res)

    return json.dumps({

    })
    
@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    
    app.run(host='0.0.0.0', debug=True, port=5000)


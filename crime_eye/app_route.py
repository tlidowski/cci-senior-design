import json

import math

import numpy as np
from flask import Flask, render_template, jsonify, request
import requests
import pandas as pd
from math import radians, cos, sin, asin, sqrt
import validation as v
import aws_connection as aws
import map_processing as mp

app = Flask(__name__)
engine = None

veryUnsafeThreshold = 2
veryUnsafeScore = 1

unsafeThreshold = 1
unsafeScore = 2

okThreshold = 0.5
okScore = 3

safeThreshold = 0.25
safeScore = 4

reallySafeScore = 5


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
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 3956  # Radius of earth in Miles. Use 3956 for miles.
    return c * r


def get_location_from_name(city):
    # Lon, Lat
    nameMap = {
        "boston": [-71.0589, 42.3601, ],
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


@app.route('/crimes_pie_chart', methods=['GET'])
def get_pie_chart():
    # pie chart using crime codes 
    # TODO: group crime codes into categories provided by prof
    crime_descriptions = {
        'Arson': ['200'],
        'Assault': ['13', '13A', '13B', '13C'],
        'Bribery': ['510'],
        'Burglary': ['220'],
        'Counterfeiting/Forgery': ['250'],
        'Vandalism of Property': ['290'],
        'Drug/Narcotic Offenses': ['35', '35A', '35B'],
        'Embezzlement': ['270'],
        'Extortion/Blackmail': ['210'],
        'Fraud Offenses': ['26', '26A', '26B', '26C', '26D', '26E'],
        'Gambling Offenses': ['39', '39A', '39B', '39C', '39D'],
        'Homicide': ['09', '09A', '09B', '09C'],
        'Kidnapping/Abduction': ['100'],
        'Larceny-Theft': ['23', '23A', '23B', '23C', '23D', '23E', '23F', '23G', '23H'],
        'Vehicle-Theft': ['240'],
        'Pornography': ['370'],
        'Prostitution': ['40', '40A', '40B'],
        'Armed Robbery': ['120'],
        'Sex Offenses, Forcible': ['11', '11A', '11B', '11C', '11D'],
        'Sex Offenses, Nonforcible': ['36A', '36B'],
        'Stolen Property Offenses': ['280'],
        'Weapon Law Violations': ['520'],
        'Other': ['90', '90A', '90B', '90C', '90D', '90E', '90F', '90G', '90H', '90I', '90J', '90Z']
    }

    city = request.args.get('city')
    start = request.args.get('start')
    end = request.args.get('end')
    try:
        engine = aws.initConnection()
        res = aws.get_crime_descriptions_and_counts(city, engine)

        engine.close()

        crimes_and_counts = {
        }
        count_sum = sum(res['crime_count'])
        for crime_codes, count in zip(res['fbi_crime_code'], res['crime_count']):
            if crime_codes == None:
                continue
            for crime_code in crime_codes:
                for key, values in zip(crime_descriptions.keys(), crime_descriptions.values()):
                    if crime_code in values:
                        if key in crimes_and_counts.keys():
                            crimes_and_counts[key] += count
                        else:
                            crimes_and_counts[key] = count

        keys_to_delete = []
        for crime, count in zip(crimes_and_counts.keys(), crimes_and_counts.values()):
            if crime == 'Other':
                continue
            if (count / count_sum * 100) <= .5:
                crimes_and_counts['Other'] += count
                keys_to_delete.append(crime)

        for crime in keys_to_delete:
            del crimes_and_counts[crime]
        return json.dumps({
            "counts": list(crimes_and_counts.values()),
            "crimes": list(crimes_and_counts.keys())
        })
    except Exception as e:
        print(f'Faliure: {e}')
        return {}


@app.route('/crimes_line_graph', methods=['GET'])
def get_line_graph():
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
            start_df = pd.read_csv(year_csvs[start], dtype=column_types)
            start_res = apply_mask(start_df, 'CITY_NAME', city);

            end_df = []
            end_res = []

            if start != end:
                end_df = pd.read_csv(year_csvs[end], dtype=column_types)
                end_res = apply_mask(end_df, 'CITY_NAME', city)

            # res = None
            if len(end_res) != 0:
                res = pd.concat([start_res, end_res], axis=0)
            else:
                res = start_res

            res['DATE_OCCURRED'] = pd.to_datetime(res['DATE_OCCURRED']).dt.strftime('%m/%Y')
            crimes_counted = res['DATE_OCCURRED'].value_counts().rename_axis('dates').sort_index().reset_index(
                name='counts')
            counts_filtered = crimes_counted[crimes_counted['counts'] > 0]

            # print(counts_filtered['counts'])
            return json.dumps({
                "counts": counts_filtered['counts'].to_list(),
                "dates": counts_filtered['dates'].to_list()
            })
    except Exception as e:
        print(f'Failure: {e}')
        return {}


# Using AWS
@app.route('/crimes_from_address', methods=['GET'])
def get_locations_given_address():
    cityMap = {
        "new york": "New York City"
    }
    cityName = request.args.get('cityName')
    if cityName.lower() in cityMap.keys():
        cityName = cityMap[cityName.lower()]
    # City name can be different than our database

    start = request.args.get('start')
    end = request.args.get('end')
    radius = int(request.args.get('radius'))
    userLat = float(request.args.get('lat'))
    userLon = float(request.args.get('lon'))

    if not v.validateYears(start, end):
        return json.dumps(
            {"errors": ["Invalid Years"]}
        )
    if not v.validateCity(cityName):
        return json.dumps(
            {"errors": ["No crime data for given city"]}
        )

    engine = aws.initConnection()
    res = aws.getCityDataGivenYears(cityName, start, end, engine)
    engine.close()
    crimeFeatures = mp.createFeatures(res, userLon, userLat, radius)
    radiusFeature = mp.generateRadiusGeoJson((userLon, userLat), radius)
    # Todo, generate list based on crime type as well as (or instead of) within radius
    return json.dumps({
        "errors": [],
        "center": {
            "coords": (userLon, userLat),
            "feature": radiusFeature,
        },
        "features": crimeFeatures,
    })


def getAreaOfCircle(radius):
    area = 0
    if type(radius) == float:
        area = math.pi * radius ** 2
    else:
        area = math.pi * (float(radius) ** 2)
    return area


def getRecordsInCircle(lat, long, area_of_circle, allRecords):
    return 60


def getSQOfCity(city):
    sq_of_city = 500000
    return sq_of_city


def getTotalCrimes(city):
    total_crimes = 100
    return total_crimes


@app.route('/get_crime_score', methods=['GET'])
def get_crime_score():
    print("AT GET CRIME SCORE")
    city = request.args.get('city')
    lat = float(request.args.get('lat'))
    long = float(request.args.get('long'))
    radius = float(request.args.get('radius'))
    area_of_circle = getAreaOfCircle(radius)
    print(city, lat, long, radius, area_of_circle)
    engine = None
    try:
        print("\nAT TRY:\n")
        engine = aws.initConnection()
        # print("Engine: ", engine)
        print("CHECK 1")
        SQ_of_city = aws.get_city_area(city, engine)
        print("CHECK 2")
        # total_crimes = aws.getCityDataGivenYears(city, engine)
        # # N = area_of_circle * total_crimes / SQ_of_city
        # # print(N)
        # # crimeScore = 0
        # engine.close()
        # print("\nAFTER CLOSE:\n")
        # allRecords = []
        # records_in_circle = getRecordsInCircle(lat, long, area_of_circle, allRecords)
        # frac = (records_in_circle / N)
    # if (frac > veryUnsafeThreshold):
    #     crimeScore = veryUnsafeScore
    # elif (frac > unsafeThreshold):
    #     crimeScore = unsafeScore
    # elif (frac > okThreshold):
    #     crimeScore = okScore
    # elif (frac > safeThreshold):
    #     crimeScore = safeScore
    # elif (frac < safeThreshold):
    #     crimeScore = reallySafeScore
    except Exception as e:
        print(f'Failure: {e}')
        return {}
    crimeScore = 1
    return json.dumps(
        {"crimeScore": crimeScore}
    )


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)

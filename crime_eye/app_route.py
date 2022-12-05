import json

import numpy as np
from flask import Flask, render_template, jsonify, request
import requests
import pandas as pd

app = Flask(__name__)


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


@app.route('/city_crime_data', methods=['GET'])
def get_city_crime_data():
    city = request.args.get('city')
    start = request.args.get('start')
    end = request.args.get('end')

    try:
        res_json = None
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
            res_json = res.to_json(orient='records')
        return res_json
    except:
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


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()

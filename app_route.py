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
    city_name = request.args.get('city_name')
    start_year = request.args.get('start_year')
    end_year = request.args.get('end_year')

    try:
        res_json = None

        path_2020 = f'combined_city_data/city_data-{2020}.csv'
        path_2021 = f'combined_city_data/city_data-{2021}.csv'

        year_csvs = {"2020": path_2020,
                     "2021": path_2021
                     }

        column_types = get_column_types()

        if (start_year in year_csvs.keys()) and (end_year in year_csvs.keys()):
            start_year_df = pd.read_csv(year_csvs[start_year],
                                        dtype=column_types
                                        )
            start_year_res = apply_mask(start_year_df, 'CITY_NAME', city_name)

            end_year_df = []
            end_year_res = []

            if start_year != end_year:
                end_year_df = pd.read_csv(year_csvs[end_year],
                                          dtype=column_types)
                end_year_res = apply_mask(end_year_df, 'CITY_NAME', city_name)

            res = None
            if len(end_year_res) != 0:
                res = pd.concat([start_year_res, end_year_res], axis=0)
            else:
                res = start_year_res

            res_json = res.to_json()

        return res_json
    except:
        return {}

@app.route('/')
def index():
    return render_template("home.html")


if __name__ == '__main__':
    app.run()

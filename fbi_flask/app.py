from flask import Flask, render_template, jsonify, request
import requests
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import csv
from bs4 import BeautifulSoup
import io
from sodapy import Socrata
app = Flask(__name__)
fbi_key = 'hjHC4nsUI0eNerFM8kxzRN3ybp1hL71JfUlen7KL'


@app.route('/crime_by_state', methods=['GET'])
def state_crime_estimate_to_from_year():
    try:
        state_abbrev = request.args.get('state')
        start = request.args.get('start')
        end = request.args.get('end')
        base = 'https://api.usa.gov/crime/fbi/sapi/api'
        summary_by_state_year = '/estimates/states/' + state_abbrev + "/" + str(start) + '/' + str(end)
        response = requests.get(base + summary_by_state_year + "?API_KEY=" + fbi_key).json()
        response["results"].sort(key=lambda x: x['year'])
        return response
    except:
        return {}


@app.route('/')
def index():
    return render_template("home.html")


if __name__ == '__main__':
    app.run()

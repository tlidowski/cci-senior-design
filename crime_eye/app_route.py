import json

import math
import random

from flask import Flask, render_template, request
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

exceptionCities={
    "Denver": {
        "codesAndDescriptions": {
            "['13A']":"aggravated-assault",
            "['280', '90Z', '39B', '39C', '39D', '510', '520', '90C', '90J', '100', '13A', '210', '26A']":"all-other-crimes",
            "['200']":"arson",        
            "['23H', '240']":"auto-theft",
            "['220']":"burglary",
            "['35A', '35B', '90G', '26A']":"drug-alcohol",
            "['23A', '23B', '23C', '23E', '23D', '23H', '23F']":"larceny",
            "['09A', '09B']":"murder",
            "['90Z', '36A', '90H', '90Z', '370', '36B', '13B']":"other-crimes-against-persons",
            "['290', '40B', '40A', '90C', '13C']":"public-disorder",
            "['120']":"robbery",
            "['11A', '11B', '11C', '11D']":"sexual-assault",
            "['23F', '240']":"theft-from-motor-vehicle",
            "":"traffic-accident",
            "['250', '90Z', '250', '26A', '26C', '26B', '90A', '26E', '26G', '270']":"white-collar-crime",
        },
        "descriptionsAndCategories":{
            "aggravated-assault":"Person",
            "all-other-crimes":"Other",
            "arson":"Property",
            "auto-theft":"Property",
            "burglary":"Property",
            "drug-alcohol":"Society",
            "larceny":"Property",
            "murder":"Person",
            "other-crimes-against-persons":"Person",
            "public-disorder":"Society",
            "robbery":"Property",
            "sexual-assault":"Person",
            "theft-from-motor-vehicle":"Property",
            "traffic-accident":"Other",
            "white-collar-crime":"Other",
        }
    }
}
# https://ucr.fbi.gov/nibrs/2018/resource-pages/crimes_against_persons_property_and_society-2018.pdf

@app.route('/crimes_pie_chart', methods=['GET'])
def get_pie_chart():
    # pie chart using crime codes 
    crime_type = {
        'Property': ['200', '220', '250', '290', '270', '210', '26', '26A', '26B', '26C', '26D', '26E', '23', '23A',
                     '23B', '23C', '23D', '23E', '23F', '23G', '23H', '240', '280'],
        'Person': ['09', '09A', '09B', '09C', '100', '11', '11A', '11B', '11C', '11D', '36A', '36B', '120', '13', '13A',
                   '13B', '13C'],
        'Society': ['35', '35A', '35B', '39', '39A', '39B', '39C', '39D', '370', '40', '40A', '40B', '520'],
        'Other': ['90', '90A', '90B', '90C', '90D', '90E', '90F', '90G', '90H', '90I', '90J', '90Z']
    }

    city = request.args.get('city')
    start = request.args.get('start')
    end = request.args.get('end')
    try:
        engine = aws.initConnection()
        res = aws.get_crime_descriptions_and_counts(city, engine, start, end)

        engine.close()
        crimeCounts = getCounts(crime_type, res)
        print(crimeCounts)

        return json.dumps({
            "property_counts": list(crimeCounts.values()),
            "property_crimes": list(crimeCounts.keys()),
        })
    except Exception as e:
        print(f'Failure: {e}')
        return {}


def getCounts(crimes, res):
    crimes_and_counts = {}
    count_sum = sum(res['crime_count'])
    for crime_codes, count in zip(res['fbi_crime_code'], res['crime_count']):
        if crime_codes == None:
            continue

        # CTRL+F FOR DENVER FIX. 
        # INSERT IT HERE. ARGS MAY NEED CHANGING, NOT SURE
        # PUT THIS FOR LOOP INSIDE AN ELSE.

        for crime_code in crime_codes:
            for key, values in zip(crimes.keys(), crimes.values()):
                if crime_code in values:
                    if key in crimes_and_counts.keys():
                        crimes_and_counts[key] += count
                    else:
                        crimes_and_counts[key] = count

    return crimes_and_counts


@app.route('/crimes_line_graph', methods=['GET'])
def get_line_graph():
    citiesList = []

    city = request.args.get('city')
    start = request.args.get('start')
    end = request.args.get('end')
    otherCities = request.args.get('otherCities').split(",")
    for x in range(len(otherCities)):
        otherCities[x] = otherCities[x].strip()
    citiesList.append(city)
    if otherCities[0] != 'null':
        citiesList.extend(otherCities)
    data = {}

    try:
        for city in citiesList:
            engine = aws.initConnection()
            res = aws.getCityDataGivenYears(city, start, end, engine)
            engine.close()

            res['date_occurred'] = pd.to_datetime(res['date_occurred']).dt.strftime('%m/%Y')
            crimes_counted = res['date_occurred'].value_counts().rename_axis('dates').sort_index().reset_index(name='counts')
            counts_filtered = crimes_counted[crimes_counted['counts'] > 0]
            data[city] = {
                "counts": counts_filtered['counts'].to_list(),
                "dates": counts_filtered['dates'].to_list()
            }

        return json.dumps(data)
    except Exception as e:
        print(f'Failure: {e}')
        return {}

@app.route('/crimes_bar_graph', methods=['GET'])
def get_bar_graph():
    city = request.args.get('city')
    city2 = request.args.get('city2')
    start = request.args.get('start')
    end = request.args.get('end')

    crimes_against = {
        'Property': ['200', '510', '220', '250', '510', '290', '250', '270', '210', '26', '26A', '26B', '26C', '26D',
                     '26E', '23', '23A', '23B', '23C', '23D', '23E', '23F', '23G', '23H', '240', '90A'],
        'Person': ['13', '13A', '13B', '13C', '39', '09', '09A', '09B', '09C', '100', '11', '11A', '11B', '11C',
                   '11D', '36', '36B'],
        'Society': ['35', '35A', '35B', '39', '39A', '39B', '39C', '39D', '40', '40A', '40B', '90B', '90C', '90D',
                    '90E', '90F', '90G', '90H', '90J', '370'],
        'Other': ['90z', '90Z', '90I']
    }
    try:
        engine = aws.initConnection()
        res = aws.get_crime_descriptions_and_counts(city, engine, start, end)
        res2 = aws.get_crime_descriptions_and_counts(city2, engine, start, end)
        engine.close()

        crimes_against_counts = {
        }
        crimes_against_counts2 = {
        }
        for crime_codes, count in zip(res['fbi_crime_code'], res['crime_count']):
            if crime_codes == None:
                continue

            # CTRL+F FOR DENVER FIX. 
            # INSERT IT HERE. ARGS MAY NEED CHANGING, NOT SURE
            # PUT THIS FOR LOOP INSIDE AN ELSE.
            for crime_code in crime_codes:
                for key, values in zip(crimes_against.keys(), crimes_against.values()):
                    if crime_code in values:
                        if key in crimes_against_counts.keys():
                            crimes_against_counts[key] += count
                        else:
                            crimes_against_counts[key] = count
        for crime_codes, count in zip(res2['fbi_crime_code'], res2['crime_count']):
            if crime_codes == None:
                continue
            # CTRL+F FOR DENVER FIX. 
            # INSERT IT HERE. ARGS MAY NEED CHANGING, NOT SURE
            # PUT THIS FOR LOOP INSIDE AN ELSE.
            for crime_code in crime_codes:
                for key, values in zip(crimes_against.keys(), crimes_against.values()):
                    if crime_code in values:
                        if key in crimes_against_counts2.keys():
                            crimes_against_counts2[key] += count
                        else:
                            crimes_against_counts2[key] = count
        return json.dumps({
            "counts": list(crimes_against_counts.values()),
            "crimes": list(crimes_against_counts.keys()),
            "counts2": list(crimes_against_counts2.values()),
            "crimes2": list(crimes_against_counts2.keys())
        })
    except Exception as e:
        print(f'Faliure: {e}')
        return {}


cityNames = [
    "Austin",
    "Baltimore",
    "Boston",
    "Charlotte",
    "Chicago",
    "Denver",
    "Detroit",
    "Los Angeles",
    "New York City",
    "Philadelphia",
    "Seattle",
    "Washington DC",
];

citiesInclusions = {}


def initializeCitiesInclusions():
    global citiesInclusions
    citiesInclusions = dict.fromkeys(cityNames, False)


initializeCitiesInclusions()

crimes_against = {
    'Property': ['200', '510', '220', '250', '510', '290', '250', '270', '210', '26', '26A', '26B', '26C', '26D',
                 '26E', '23', '23A', '23B', '23C', '23D', '23E', '23F', '23G', '23H', '240', '90A'],
    'Person': ['13', '13A', '13B', '13C', '39', '09', '09A', '09B', '09C', '100', '11', '11A', '11B', '11C',
               '11D', '36', '36B'],
    'Society': ['35', '35A', '35B', '39', '39A', '39B', '39C', '39D', '40', '40A', '40B', '90B', '90C', '90D',
                '90E', '90F', '90G', '90H', '90J', '370'],
    'Other': ['90z', '90Z', '90I']
}

def getCategoryGivenCityCrimeCode(city, crime_codes_str):
    exceptionCityInfo = exceptionCities[city]
    description = exceptionCityInfo["codesAndDescriptions"][crime_codes_str]
    category = exceptionCityInfo["descriptionsAndCategories"][description]
    return category
    

@app.route('/crimes_stacked_bar_graph', methods=['GET'])
def get_stacked_bar_graph():
    citiesList = []

    city = request.args.get('city')
    start = request.args.get('start')
    end = request.args.get('end')
    otherCitiesDict = json.loads(request.args.get('otherCities'))
    otherCities = []
    otherCities = otherCitiesDict["other_cities"]

    citiesList.append(city)
    citiesList.extend(otherCities)

    engine = aws.initConnection()
    crimes_against_counts_per_city = {}
    for city in citiesList:
        if (citiesInclusions[city] == False):
            res = aws.get_crime_descriptions_and_counts(city, engine, start, end)
            crimes_against_counts_per_city[city] = {}
            citiesInclusions[city] == True
            codeCountZip = zip(res['fbi_crime_code'], res['crime_count'])
            
            for crime_codes, count in codeCountZip:
                if crime_codes == None:
                    continue
                ##===========START DENVER FIX=============
                if city in exceptionCities: #<--------if condition was added
                    category = getCategoryGivenCityCrimeCode(city, str(crime_codes))
                    if category in crimes_against_counts_per_city[city].keys():
                        crimes_against_counts_per_city[city][category] += count
                    else:
                         crimes_against_counts_per_city[city][category] = count
                ##===========END DENVER FIX=============
                else: #<-----------else condition was added around the existing for condition
                    for crime_code in crime_codes:
                        for category, codes in zip(crimes_against.keys(), crimes_against.values()):
                            if crime_code in codes:
                                if category in crimes_against_counts_per_city[city].keys():
                                    crimes_against_counts_per_city[city][category] += count
                                else:
                                    crimes_against_counts_per_city[city][category] = count
    engine.close()
    return json.dumps(crimes_against_counts_per_city)


# Using AWS
@app.route('/crimes_from_address', methods=['GET'])
def get_locations_given_address():
    cityMap = {
        "new york": "New York City",
        "washington": 'Washington DC',
    }
    cityName = request.args.get('cityName')
    if cityName.lower() in cityMap.keys():
        cityName = cityMap[cityName.lower()]
    # City name can be different from our database

    start = request.args.get('start')
    end = request.args.get('end')
    dropdownCity = request.args.get('dropdownCity')
    radius = int(request.args.get('radius'))
    userLat = float(request.args.get('lat'))
    userLon = float(request.args.get('lon'))

    if not v.validateYears(start, end):
        return json.dumps(
            {"errors": ["Invalid Years"]}
        )
    if dropdownCity == "Select City":
        return json.dumps(
            {"errors": ["Please select a city from the dropdown first"]}
        )
    if not v.validateCity(cityName, dropdownCity):
        return json.dumps(
            {"errors": ["Address must be in selected city"]}
        )

    engine = aws.initConnection()

    res = aws.getCityDataGivenYears(cityName, start, end, engine)
    ret = aws.get_city_area(cityName, engine)
    SQ_of_city = ret["area"].tolist()[0]

    pop = aws.get_city_population(cityName, engine)
    cityPop = pop["population"].tolist()[0]

    crimes = aws.get_total_city_crimes(cityName, engine)
    totalCrimes = crimes["count"].tolist()[0]

    engine.close()

    crimeFeatures = mp.createFeatures(res, userLon, userLat, radius)
    area_of_circle = getAreaOfCircle(radius)
    crimeScore = -1
    crimeScoreLabel = ""
    crimeRate = -1
    crimeRateLabel = "per 1000 people"

    try:
        crimeRate = calculateCrimeRate(cityPop, totalCrimes)
        total_crimes = len(crimeFeatures["inside"]) + len(crimeFeatures["outside"])
        N = area_of_circle * total_crimes / SQ_of_city
        records_in_circle = len(crimeFeatures["inside"])
        frac = (records_in_circle / N)
        if (frac > veryUnsafeThreshold):
            crimeScore = veryUnsafeScore
            crimeScoreLabel = "Very Unsafe"
        elif (frac > unsafeThreshold):
            crimeScore = unsafeScore
            crimeScoreLabel = "Unsafe"
        elif (frac > okThreshold):
            crimeScore = okScore
            crimeScoreLabel = "Ok"
        elif (frac > safeThreshold):
            crimeScore = safeScore
            crimeScoreLabel = "Safe"
        elif (frac < safeThreshold):
            crimeScore = reallySafeScore
            crimeScoreLabel = "Very Safe"
    except Exception as e:
        return json.dumps({
            "errors": [e],
        })

    radiusFeature = mp.generateRadiusGeoJson((userLon, userLat), radius)
    return json.dumps({
        "errors": [],
        "center": {
            "coords": (userLon, userLat),
            "feature": radiusFeature,
        },
        "features": crimeFeatures,
        "crimeScore": crimeScore,
        "crimeScoreLabel": crimeScoreLabel,
        "crimeRate": crimeRate,
        "crimeRateLabel": crimeRateLabel
    })


def get_crime_rate(cityName):
    try:
        cityMap = {
            "new york": "New York City",
            "washington": 'Washington DC',
        }
        if cityName.lower() in cityMap.keys():
            cityName = cityMap[cityName.lower()]
        current_engine = aws.initConnection()
        pop = aws.get_city_population(cityName, current_engine)
        cityPop = pop["population"].tolist()[0]
        crimes = aws.get_total_city_crimes(cityName, current_engine)
        totalCrimes = crimes["count"].tolist()[0]
        current_engine.close()
        crimeRate = calculateCrimeRate(cityPop, totalCrimes)
        return crimeRate
    except:
        return 'error'


@app.route('/crimes_rate_given_city', methods=['GET'])
def crimes_rate_given_city():
    city_name = request.args.get('cityName')
    cities = json.loads(request.args.get('cities'))
    if cities:
        cities = cities.split(', ')
        if city_name not in cities:
            cities = [city_name] + cities
        elif len(cities) == 1:
            crime_rate = get_crime_rate(city_name)
            return json.dumps({
                "crimeRate": crime_rate,
            })
        crime_rate_map = []
        for current_city_name in cities:
            crime_rate_map.append({'cityName': current_city_name, 'crimeRate': get_crime_rate(current_city_name)})
        return json.dumps({
            "crimeRateMap": crime_rate_map,
        })
    else:
        crime_rate = get_crime_rate(city_name)
        return json.dumps({
            "crimeRate": crime_rate,
        })


@app.route('/area_population_given_city', methods=['GET'])
def get_population_to_area_crimes():
    city_name = request.args.get('cityName')
    cities = json.loads(request.args.get('cities'))
    cities = cities.split(', ')
    if city_name not in cities:
        cities = [city_name] + cities
    currentEngine = aws.initConnection()
    df = aws.getAllCityMetaData(currentEngine)
    df = df.loc[df['city_name'].isin(cities)]
    info = {'x': df['area'].to_list(), 'y': df['population'].to_list(), 'mode': 'markers',
            'text': df['city_name'].to_list()}
    marker = {'color': [], 'opacity': [], 'size': []}
    crime_rates = [get_crime_rate(info['text'][i]) for i in range(len(info['text']))]
    most_crime = max(crime_rates)
    for i in range(len(cities)):
        r = str(random.randint(1, 255))
        g = str(random.randint(1, 255))
        b = str(random.randint(1, 255))
        color = 'rgb({}, {}, {})'.format(r, g, b)
        marker['color'].append(color)
        marker['opacity'].append(crime_rates[i] / most_crime)
        marker['size'].append(30)
    info['marker'] = marker
    currentEngine.close()
    return json.dumps({
        "info": info,
    })


def calculateCrimeRate(population, total):
    rate = total / population
    perThousand = rate * 1000
    return round(perThousand, 2)


def getAreaOfCircle(radius):
    area = 0
    if type(radius) == float:
        area = math.pi * radius ** 2
    else:
        area = math.pi * (float(radius) ** 2)
    return area


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)

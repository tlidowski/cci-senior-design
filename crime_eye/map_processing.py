from math import radians, cos, sin, asin, sqrt, pi
import numpy as np
import pandas as pd

crimes_against = {
        'Property': ['200', '510', '220', '250', '510', '290', '250', '270', '210', '26', '26A', '26B', '26C', '26D',
                     '26E', '23', '23A', '23B', '23C', '23D', '23E', '23F', '23G', '23H', '240', '90A'],
        'Person': ['13', '13A', '13B', '13C', '39', '09', '09A', '09B', '09C', '100', '11', '11A', '11B', '11C',
                   '11D', '36', '36B'],
        'Society': ['35', '35A', '35B', '39', '39A', '39B', '39C', '39D', '40', '40A', '40B', '90B', '90C', '90D',
                    '90E', '90F', '90G', '90H', '90J', '370'],
        'Other': ['90z', '90Z', '90I']
    }



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

def getCrimeCategory(code):
    if not code:
        return "NotFound"
    for i, (key, val) in enumerate(crimes_against.items()):
        if code in val:
            return key
    return "NotFound"

# Returns a list of features for the mapChart's sources
def createFeatures(res, userLon, userLat, radius):
    features = {
                "inside": [],
                "outside": []
            }
    for i, row in res.iterrows():
        if not (np.isnan(row["longitude"]) and np.isnan(row["latitude"])):
            # return 2 separate lists of latitudes and longitudes based off whether they are within the radius
            lat = row["latitude"]
            lon = row["longitude"]
            crimeCode = row["fbi_crime_code"]
            crimeType = "NotFound"
            if crimeCode:
                crimeType = getCrimeCategory(row["fbi_crime_code"][0])
            tempFeature = {
                "type": 'Feature',
                "geometry" : {
                    "type": "Point",
                    "coordinates": (lon, lat)
                },
                "properties": {
                    "crimeType": crimeType
                },
            }
            if haversine(userLon, userLat, lon, lat) <= radius:
                features["inside"].append(tempFeature)
            else:
                features["outside"].append(tempFeature)
    return features

def generateRadiusGeoJson(center, radiusInMiles, points=None):
    if not points:
        points = 64

    coords = {
        "latitude": center[1],
        'longitude': center[0]
    }

    km = radiusInMiles * 1.609344

    ret = []
    distanceX = km/(111.320*cos(coords['latitude']*pi/180))
    distanceY = km/110.574

    for i in range(points):
        theta = (i/points)*(2*pi)
        x = distanceX*cos(theta)
        y = distanceY*sin(theta)

        ret.append([coords['longitude'] + x, coords['latitude']+y])
    
    ret.append(ret[0])

    return {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [ret]
            }
        }]
    }
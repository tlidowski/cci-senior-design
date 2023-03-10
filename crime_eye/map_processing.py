from math import radians, cos, sin, asin, sqrt, pi
import numpy as np
import pandas as pd

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
            tempFeature = {
                "type": 'Feature',
                "geometry" : {
                    "type": "Point",
                    "coordinates": (lon, lat)
                },
                "properties": {
                    "description": "CRIME TYPE"
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
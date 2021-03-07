#%%
import requests
import json
import ast
# from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from PIL import Image

'''
Function Definitions
'''

def LatLonInput(): # Function for taking in lat/lon user input
    lat = False
    lon = False

    # Make sure inputs are within proper range
    while not lat:
        try:
            tempLat = float(input("Enter your latitude: "))  # Gather latitude
        except ValueError: # If user doesn't input a number catch the fault and have them try again
            print("ERROR: Latitude must be a numerical value between -90 and 90 degrees. ")
            continue
        if tempLat < -90 or tempLat > 90:
            # Check that input is within latitude range
            print("ERROR: Latitude must be a numerical value between -90 and 90 degrees. ")
        else:
            # If input passes all checks, assign input to latitude var
            lat = tempLat

    while not lon:
        try:
            tempLon = float(input("Enter your longitude: ")) # Gather longitude
        except ValueError: # If user doesn't input a number catch the fault and have them try again
            print("ERROR: Longitude must be a numerical value between -180 and 180 degrees. ")
            continue
        if tempLon < -180 or tempLon > 180:
            # Check that input is within longitude range
            print("ERROR: Longitude must be a numerical value between -180 and 180 degrees. ")
        else:
            # If input passes all checks, assign input to longitude var 
            lon = tempLon

    # print(lat, lon) # Print collected values to make sure they are being collected properly
    return lat, lon

def getIATA(lat, lon):
    url = "http://iatageo.com/getCode/" + str(lat) + "/" + str(lon)
    req = requests.get(url)
    return json.dumps(req.json(), sort_keys=True)

def changeM2Lat(M):
    R = 3960
    rad2deg = 180/math.pi
    return (M/R)*rad2deg

def changeM2Lon(lat, M):
    R = 3960
    deg2rad = math.pi/180
    rad2deg = 180/math.pi
    r = R*math.cos(lat*deg2rad)
    return (M/r)*rad2deg

def openskyAPICurrStatus():
    # Test lat and lon of Boulder, CO
    # lat = 40.016869
    lat = 33.9416
    # lon = -105.279617
    lon = -118.4085
    M = 25
    minLat = lat-changeM2Lat(M)
    minLon = lon-changeM2Lon((lat + changeM2Lat(M)) if lat > 0 else (lat-changeM2Lat(M)), M)
    maxLat = lat+changeM2Lat(M)
    maxLon = lon+changeM2Lon((lat + changeM2Lat(M)) if lat > 0 else (lat-changeM2Lat(M)), M)

    request_parameters = {
        "lamin": str(minLat),
        "lomin": str(minLon),
        "lamax": str(maxLat),
        "lomax": str(maxLon)
    }
    url = "https://opensky-network.org/api/states/all"
    req = requests.get(url, params=request_parameters)

    plane_library = json.loads(req.text)
    # print(type(ast.literal_eval(plane_library)))
    # print(len(plane_library[1]))
    with open("opensky.json", "w") as outfile:
        json.dump(plane_library, outfile)
    
    return plane_library

def screenOut(lat, lon):
    #64x48
    # baseLat = 40.016869
    baseLat = 33.9416
    # baseLon = -105.279617
    baseLon = -118.4085
    M = 25
    minLat = baseLat-changeM2Lat(M)
    maxLat = baseLat+changeM2Lat(M)
    minLon = baseLon-changeM2Lon((baseLat + changeM2Lat(M)) if baseLat > 0 else (baseLat-changeM2Lat(M)), M)
    maxLon = baseLon+changeM2Lon((baseLat + changeM2Lat(M)) if baseLat > 0 else (baseLat-changeM2Lat(M)), M)

    modLat = []
    modLon = []

    for i in lat:
        # Latitude array
        modLat.append(int(48 * ((i-minLat)/(maxLat-minLat))))
    for i in lon:
        # Longitude array
        modLon.append(int(64 * ((i-minLon)/(maxLon-minLon))))
    
    out = []
    for i in range(len(lat)):
        out.append([modLat[i], modLon[i]])
    
    f = open("rpdata.txt", "w")
    f.write(str(out))
    f.close()
    return

def plotPlanes(lat, lon, dictionary):
    # lat = 40.016869
    lat = 33.9416
    # lon = -105.279617
    lon = -118.4085
    M = 25
    
    minLat = lat-changeM2Lat(M)
    minLon = lon-changeM2Lon((lat + changeM2Lat(M)) if lat > 0 else (lat-changeM2Lat(M)), M)
    maxLat = lat+changeM2Lat(M)
    maxLon = lon+changeM2Lon((lat + changeM2Lat(M)) if lat > 0 else (lat-changeM2Lat(M)), M)

    latCoords = []
    lonCoords = []
    altitude = []
    trueTrack = []

    for x in dictionary["states"]:
        if x[7]:
            latCoords.append(float(x[6]))
            lonCoords.append(float(x[5]))
            altitude.append(float(x[7]))
            trueTrack.append(float(x[10] if x[10] else 0))

    screenOut(latCoords, lonCoords)

    BBox = [minLon, maxLon, minLat, maxLat]
    
    fig, ax = plt.subplots(figsize = (8,7))

    for x in range(len(lonCoords)):
        ax.scatter(lonCoords[x], latCoords[x], zorder = 1, alpha = 1, s = 50, c = '#000000', marker = (3, 0 , trueTrack[x]))
    
    ax.scatter(lon, lat, s = 20, c = '#FF0000', marker = "o")

    ax.scatter(lon, lat, s = 1000, edgecolors = '#0000FF', marker = "o", facecolors = 'none')
    ax.scatter(lon, lat, s = 10000, edgecolors = '#0000FF', marker = "o", facecolors = 'none')
    ax.scatter(lon, lat, s = 45000, edgecolors = '#0000FF', marker = "o", facecolors = 'none')
    ax.scatter(lon, lat, s = 100000, edgecolors = '#0000FF', marker = "o", facecolors = 'none')
    ax.scatter(lon, lat, s = 190000, edgecolors = '#0000FF', marker = "o", facecolors = 'none')

    ax.set_title('Planes Above Me')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_xlim(BBox[0], BBox[1])
    ax.set_ylim(BBox[2], BBox[3])  

    fig = plt.figure()
    plt.savefig("planesPlot.png", dpi=10)
    plt.show()
    return

'''
Main Function
'''

dictionary = openskyAPICurrStatus()
plotPlanes(0, 0, dictionary)

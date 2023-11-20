import math
import requests
import io
from PIL import Image
import geopy
from latlonRect import LatLonRect
import numpy as np




def degrees_to_tilenums(lat_deg : float, lon_deg : float, zoom : int) -> (int, int):
    lat_rad = math.radians(lat_deg)
    n = 1 << zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile

def tilenums_to_degrees(x, y, zoom):
    n = 1 << zoom
    lon_deg = x / n * 360.0 - 180.0
    lat_deg = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    return lat_deg, lon_deg

def test():
    zoom = 14
    for x in range(-2000, 2000, 100):
        for y in range(0, 7000, 100):
            lat, lon = tilenums_to_degrees(x, y, zoom)
            xx, yy = degrees_to_tilenums(lat, lon, zoom)
            if (xx != x) or (yy != y):
                print(f"({x}, {y}) => ({xx}, {yy})")
            else:
                print(".")

if __name__ == '__main__':
    test()# def get_rect_coordinates(top_left : geopy.point.Point, width : geopy.distance.distance, height : geopy.distance.distance) -> LatLonRect:
#     top_right =


# https://api.mapbox.com/styles/v1/glogfogle/cln9sr76k008w01pu4zcc9f1b.html?title=view&access_token=pk.eyJ1IjoiZ2xvZ2ZvZ2xlIiwiYSI6ImNsbjR5aGRreDAzZHUycG8wcmwxbmlqajIifQ.3_3Lld014R3eQKiGAjl7Gg&zoomwheel=true&fresh=true#16.78/45.540486/-122.630553
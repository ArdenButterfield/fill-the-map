import geopy


class LatLonRect:
    def __init__(self, top_left : geopy.point.Point,
                 top_right : geopy.point.Point,
                 bottom_left : geopy.point.Point,
                 bottom_right : geopy.point.Point):
        self.top_left = top_left
        self.top_right = top_right
        self.bottom_left = bottom_left
        self.bottom_right = bottom_right

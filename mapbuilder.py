from tilesource import degrees_to_tilenums, tilenums_to_degrees
from detectTrees import detect_trees
import scipy
from tqdm import tqdm

from secrets import MAPBOX_ACCESS_TOKEN
import requests
from PIL import Image
import io
import numpy as np
import matplotlib.pyplot as plt
import geopy
import json
import os.path

DOWNSCALED_SIZE = 256

class MapBuilder:
    zoom = 14

    images_dir = "./images/"

    WE_ARE_HERE = geopy.point.Point(45.54, -122.62)
    HELENS = geopy.point.Point(46.21, -122.23)
    SEATTLE = geopy.point.Point(47.60, -122.33)
    EUGENE = geopy.point.Point(44.04, -123.10)
    HONOLULU = geopy.point.Point(21.27, -157.82)
    FOREST_GROVER = geopy.point.Point(45.52,-123.11)
    SPRINGFIELD = geopy.point.Point(44.04,-123.03)
    def api_call(self, x, y, style, savedir, zoom=14):
        savepath = f"{self.images_dir}{savedir}/{zoom}-{x}-{y}.png"
        if os.path.isfile(savepath):
            return np.array(Image.open(savepath))
        url = f"https://api.mapbox.com/styles/{style}/tiles/512/{zoom}/{x}/{y}@2x?access_token={MAPBOX_ACCESS_TOKEN}"
        result = requests.get(url)
        if result.ok:
            image = Image.open(io.BytesIO(result.content)).convert('RGB')
            image.save(savepath)
            arr = np.array(image)
            return arr
        else:
            raise ValueError(result.reason)

    def get_background(self, x, y):
        destdir = "background"
        return self.api_call(x, y, 'v1/glogfogle/clobqstdx00b501rcezyd1q7u', destdir)

    def get_shading(self, x, y):
        destdir = "shading"
        return self.api_call(x, y, 'v1/glogfogle/clobt7aov00bt01mv4q6j05zg', destdir)

    def get_buildings(self, x, y):
        destdir = "buildings"
        big = np.zeros((1024 * 2, 1024 * 2, 3))
        big[:1024, :1024] = self.api_call(x * 2, y * 2, "v1/glogfogle/cloc4g0ho00bv01mv44t40cqr", destdir,
                                          zoom=self.zoom + 1)
        big[:1024, 1024:] = self.api_call(x * 2 + 1, y * 2, "v1/glogfogle/cloc4g0ho00bv01mv44t40cqr", destdir,
                                          zoom=self.zoom + 1)
        big[1024:, :1024] = self.api_call(x * 2, y * 2 + 1, "v1/glogfogle/cloc4g0ho00bv01mv44t40cqr", destdir,
                                          zoom=self.zoom + 1)
        big[1024:, 1024:] = self.api_call(x * 2 + 1, y * 2 + 1, "v1/glogfogle/cloc4g0ho00bv01mv44t40cqr", destdir,
                                          zoom=self.zoom + 1)

        normal_size = big[::2, ::2]
        return ~normal_size[:,:,1].astype(bool)


        #
        # toplat, leftlon = tilenums_to_degrees(x, y, self.zoom)
        # bottomlat, rightlon = tilenums_to_degrees(x + 1, y + 1, self.zoom)
        # print(bottomlat, leftlon, toplat, rightlon)
        # query = (f"https://overpass-api.de/api/interpreter?data=%5Bout%3Ajson%5D%5Bbbox%3A{bottomlat}%2C%20"
        #          f"{leftlon}%2C%20{toplat}%2C%20{rightlon}%5D%3B%0A%0A%0Away%20%5B%22building%22%5D%3B%"
        #          f"0A%2F%2F%20relation%20%5B%22building%22%5D%3B%0A%2F%2F%20way%28r%29%5B%21%22building%3Apart%22%5D%3B"
        #          f"%0Aout%20geom%3B%0A")
        # result = requests.get(query)
        # if result.ok:
        #     data = json.loads(result.content)
        #     for element in data["elements"]:
        #         points = element["geometry"]
        #         # https://stackoverflow.com/questions/16625507/checking-if-a-point-is-inside-a-polygon/23453678#23453678
        # else:
        #     raise ValueError(result.reason)
        # return self.api_call(x, y, "v1/glogfogle/cloc4g0ho00bv01mv44t40cqr", destination)

    def get_satellite(self, x, y):
        destdir = "satellite"
        return self.api_call(x, y, 'v1/glogfogle/cloc5tmsz00cx01q2dbm75fmg', destdir)


    def get_trees(self, x, y):
        return detect_trees(self.get_satellite(x, y))

    def get_tile(self, x, y):
        shadow_kernel = [
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,1]
        ]
        savepath = f"{self.images_dir}complete/14-{x}-{y}.png"
        if os.path.isfile(savepath):
            return np.array(Image.open(savepath))
        im = self.get_background(x, y)
        sat = self.get_satellite(x, y)
        buildings = self.get_buildings(x, y)
        buildingshadow = scipy.signal.convolve2d(buildings.astype(np.uint8), shadow_kernel, mode='same') > 0
        im[buildingshadow] = [0,0,0]
        im[buildings] = sat[buildings]
        trees = self.get_trees(x, y)
        treeshadow = scipy.signal.convolve2d(trees.astype(np.uint8), shadow_kernel, mode='same') > 0
        im[treeshadow] = [0,0,0]
        im[trees] = [46, 153, 34]
        shading = self.get_shading(x, y)

        darken = shading[:,:,0].repeat(3,axis=1).reshape(im.shape)
        lighten = shading[:,:,1].repeat(3,axis=1).reshape(im.shape)
        im = im.astype(np.int16)
        im += lighten
        im -= darken
        im[im > 255] = 255
        im[im < 0] = 0
        im = im.astype(np.uint8)
        image = Image.fromarray(im)
        image.save(savepath)

        return im

    def get_downscaled_tile(self, x, y):
        savepath = f"{self.images_dir}downscaled/14-{x}-{y}.png"
        if os.path.isfile(savepath):
            return np.array(Image.open(savepath))
        im = self.get_tile(x, y)
        downscaled = im[::4, ::4]
        image = Image.fromarray(downscaled)
        image.save(savepath)

        return downscaled

    def get_tiles_around(self, lat, lon, width, height):
        x, y = degrees_to_tilenums(lat, lon, self.zoom)
        dest = np.zeros((height * DOWNSCALED_SIZE, width * DOWNSCALED_SIZE, 3), dtype=np.uint8)
        for i in tqdm(range(height)):
            for j in range(width):
                tile = self.get_downscaled_tile(x + j - width // 2, y + i - height // 2)
                yy = i * DOWNSCALED_SIZE
                xx = j * DOWNSCALED_SIZE
                dest[yy:yy+DOWNSCALED_SIZE, xx:xx+DOWNSCALED_SIZE] = tile
        return dest

    def main(self):
        around = self.get_tiles_around(self.SPRINGFIELD.latitude, self.SPRINGFIELD.longitude, 4, 4)
        image = Image.fromarray(around)
        image.save("springfield.png")
        # %%


if __name__ == '__main__':
    a = MapBuilder()
    a.main()

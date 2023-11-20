import os
from PIL import Image
import numpy as np
import base64
import json

out = {}

downscaled_dir = 'images/downscaled'
for image in os.listdir(downscaled_dir):
    data = np.array(Image.open(downscaled_dir + '/' + image).convert('RGB'), dtype=np.uint8)
    stripped_name = image[3:-4]
    print(stripped_name)
    encoded = base64.b64encode(data)
    out[stripped_name] = encoded.decode()

r = json.dumps(out)
r = "export const mapdata = " + r + ";"
with open('website/public/static/scripts/mapdata.js', 'w') as f:
    f.write(r)

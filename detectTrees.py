import matplotlib
import numpy as np
import scipy

greenkernel = """
.........
.........
.........
..#####..
..#####..
..#####..
..#####..
.........
.........
"""
shadowkernel = """
.........
.........
.........
.........
.........
###...###
#########
#########
#########
"""

treefilloutkernel = """
.###.
#####
#####
#####
.###.
"""

greenkernel = [[i == "#" for i in row] for row in greenkernel.split("\n")[1:-1]]
shadowkernel = [[i == "#" for i in row] for row in shadowkernel.split("\n")[1:-1]]
treefilloutkernel = [[i == "#" for i in row] for row in treefilloutkernel.split("\n")[1:-1]]

def detect_trees(sat):
    rows = len(sat)
    cols = len(sat[0])
    hsvsat = matplotlib.colors.rgb_to_hsv(sat.astype("float") / 256)
    greenmask = np.ones((rows, cols), dtype="bool")
    greenmask *= 0.25 < hsvsat[:, :, 0]  # Hue
    greenmask *= hsvsat[:, :, 0] < 0.33
    greenmask *= 0.1 < hsvsat[:, :, 1]  # value
    greenmask *= hsvsat[:, :, 1] < 0.5
    greenmask *= 0.1 < hsvsat[:, :, 2]  # saturation
    greenmask *= hsvsat[:, :, 2] < 0.55

    greenonly = sat.copy()
    greenonly[~greenmask] = [255, 255, 255]

    shadowmask = np.ones((rows, cols), dtype="bool")
    shadowmask *= hsvsat[:, :, 2] < 0.15

    shadowonly = sat.copy()
    shadowonly[~shadowmask] = [255, 255, 255]

    greenscore = scipy.signal.convolve2d(greenmask.astype("uint8"), greenkernel, mode='same')
    shadowscore = scipy.signal.convolve2d(shadowmask.astype("uint8"), shadowkernel, mode='same')
    treescore = (greenscore > 3) * (shadowscore > 3)

    return scipy.signal.convolve2d(treescore.astype("uint8"), treefilloutkernel, mode='same') > 0

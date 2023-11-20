const MAP_WIDTH_PIXELS = 256;
const MAP_HEIGHT_PIXELS = 256;

let visited = {};

const ZOOM = 14

let currentTile = {
    x: -1,
    y: -1
}

import {mapdata} from './mapdata.js';

function latlonToTileCoords(position, zoom=ZOOM) {
    let lat_rad = position.coords.latitude * 2 * Math.PI / 360;
    let n = 1 << zoom;
    let xtile = (position.coords.longitude + 180) / 360 * n;
    let ytile = (1 - Math.asinh(Math.tan(lat_rad)) / Math.PI) / 2 * n;
    return {x: xtile, y: ytile}
}

function getTile(position, zoom=ZOOM) {
    let pos = latlonToTileCoords(position, zoom);
    return {x: Math.floor(pos.x), y: Math.floor(pos.y)};
}

function getPositionWithinTile(position, zoom=ZOOM) {
    let pos = latlonToTileCoords(position, zoom);
    return {x: pos.x % 1, y: pos.y % 1};
}

function componentToHex(c) {
    // credit: https://stackoverflow.com/questions/5623838/rgb-to-hex-and-hex-to-rgb
    var hex = c.toString(16);
    return hex.length === 1 ? "0" + hex : hex;
}

function getTilename(tile) {
    return tile.x + '-' + tile.y;
}

function getTileData(tileCoord) {
    name = getTilename(tileCoord);
    let tileData = [];
    if (mapdata.hasOwnProperty(name)) {
        let pixdata = Uint8Array.from(atob(mapdata[name]), c => c.charCodeAt(0));
        for (let y = 0; y < MAP_HEIGHT_PIXELS; y++) {
            tileData[y] = []
            for (let x = 0; x < MAP_WIDTH_PIXELS; x++) {
                let pos = (y * MAP_WIDTH_PIXELS + x) * 3;
                let r = pixdata[pos];
                let g = pixdata[pos + 1];
                let b = pixdata[pos + 2];
                tileData[y][x] = "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
            }
        }
    } else {
        for (let y = 0; y < MAP_HEIGHT_PIXELS; y++) {
            tileData[y] = []
            for (let x = 0; x < MAP_WIDTH_PIXELS; x++) {
                tileData[y][x] = "#000000";
            }
        }

    }
    return tileData
}

function displayTile(tile) {
    let tileData = getTileData(tile);
    currentTile.x = tile.x;
    currentTile.y = tile.y;
    const visitedGrid = visited[getTilename(tile)];

    for (let canvas of document.getElementsByClassName("map-canvas")) {
        if (canvas.getContext) {
            const ctx = canvas.getContext("2d");
            for (let y = 0; y < MAP_HEIGHT_PIXELS; y++) {
                for (let x = 0; x < MAP_WIDTH_PIXELS; x++) {
                    let pos = (y * MAP_WIDTH_PIXELS + x);
                    let color;
                    if (visitedGrid[y][x]) {
                        color = tileData[y][x];
                    } else {
                        if (y % 2 === x % 2) {
                            color = "beige";
                        } else {
                            color = "tan";
                        }
                    }
                    ctx.fillStyle = color;
                    ctx.fillRect(x, y, 1, 1);
                }
            }
        }
    }
}

function makeBlankVisitedGrid() {
    let grid = []
    for (let y = 0; y < MAP_HEIGHT_PIXELS; ++y) {
        grid[y] = []
        for (let x = 0; x < MAP_WIDTH_PIXELS; ++x) {
            grid[y][x] = false;
        }
    }
    return grid;
}

function visit(tile, pixelY, pixelX) {
    const visitMask = [
        ".......#######.......",
        ".....###########.....",
        "....#############....",
        "...###############...",
        "..#################..",
        ".###################.",
        ".###################.",
        "#####################",
        "#####################",
        "#####################",
        "#####################",
        "#####################",
        "#####################",
        "#####################",
        ".###################.",
        ".###################.",
        "..#################..",
        "...###############...",
        "....#############....",
        ".....###########.....",
        ".......#######.......",
    ]

    let maskCenter = {
        x: 10,
        y: 10
    }

    let tileName = getTilename(tile);
    if (!visited.hasOwnProperty(tileName)) {
        visited[tileName] = makeBlankVisitedGrid();
    }
    let grid = visited[tileName];
    for (let y = 0; y < visitMask.length; ++y) {
        for (let x = 0; x < visitMask[1].length; ++x) {
            let py = y + pixelY - maskCenter.y;
            let px = x + pixelX - maskCenter.x;
            if (visitMask[y][x] === "#" && 0 <= py && py < MAP_HEIGHT_PIXELS && 0 <= px && px < MAP_WIDTH_PIXELS) {
                grid[py][px] = true;
            }
        }
    }
}

function updatePosition(position) {
    let posWithin = getPositionWithinTile(position);
    let pixelX = Math.round(posWithin.x * MAP_WIDTH_PIXELS);
    let pixelY = Math.round(posWithin.y * MAP_HEIGHT_PIXELS);
    pixelX += MAP_WIDTH_PIXELS;
    pixelX %= MAP_WIDTH_PIXELS;
    pixelY += MAP_HEIGHT_PIXELS;
    pixelY %= MAP_HEIGHT_PIXELS;
    document.getElementById("latlon").innerText = position.coords.latitude + " " + position.coords.longitude + "(" + pixelX + " " + pixelY + ")";

    let tile = getTile(position);
    visit(tile, pixelY, pixelX);
    displayTile(tile);
}
window.onload = function () {
    for (let y = 0; y < MAP_HEIGHT_PIXELS; y++) {
        let row = []
        for (let x = 0; x < MAP_WIDTH_PIXELS; x++) {
            row[x] = false;
        }
        visited[y] = row;
    }
    if (navigator.geolocation) {

        navigator.geolocation.watchPosition(updatePosition,
            function error(msg) {alert('Please enable gps.');},
        {maximumAge:10000, timeout:5000, enableHighAccuracy: true});

    } else {
        document.getElementById("title").innerText = "Geolocation is not supported by this browser.";
    }

    for (let canvas of document.getElementsByClassName("map-canvas")) {
        canvas.width = MAP_WIDTH_PIXELS;
        canvas.height = MAP_HEIGHT_PIXELS;
    }

}

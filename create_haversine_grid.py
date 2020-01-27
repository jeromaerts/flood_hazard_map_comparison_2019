"""
Author: Jerom Aerts
Contact: j.p.m.aerts@tudelft.nl

Description:
This script creates a Haversine grid with accurate cell sizes in km2 and is necessary for inundated area calculation.
"""
import math
import numpy as np
import os
import rasterio

os.chdir('')  # set working directory

# Haversine Method
def latlon_distance(lon1, lat1, lon2, lat2, R=6372.8):
    """calculate the distance between two points (lon1, lat1) and (lon2, lat2)
    defined in latitude longitude coordinates (epsg 4326).
    :param R:   radius earth in local unit (R = 6373 for km)
    https://gist.github.com/rochacbruno/2883505"""

    degrees_to_radians = math.pi / 180.0

    phi1 = (90.0 - lat1) * degrees_to_radians
    phi2 = (90.0 - lat2) * degrees_to_radians

    theta1 = lon1 * degrees_to_radians
    theta2 = lon2 * degrees_to_radians

    cos = (math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2) + math.cos(phi1) * math.cos(
        phi2))  # multiply arc by the radius of the earth in local units to get length.

    return math.acos(cos) * R


def create_haversine_grid(file2copy, output_filename):
    """creates haversine grid based on the transform of a specified file [file2copy]."""

    # Haversine grid settings copied from file2copy.
    with rasterio.open(file2copy) as src:
        bounds = src.bounds
        shape = src.shape

    lon1 = bounds[0]
    lat1 = bounds[1]
    lon2 = bounds[2]
    lat2 = bounds[3]

    lat_cells = shape[0]
    lon_cells = shape[1]

    res_degree = (lat2 - lat1) / lat_cells

    haversine_grid = np.empty([0, 0])

    # Loop for calculating cell_area using Haversine method and constructing Haversine grid.
    for i in range(lat_cells):
        cell_width = latlon_distance(0, lat1 + (i * res_degree), res_degree, lat1 + (i * res_degree))
        cell_length = latlon_distance(lon1 + (i * res_degree), 0, lon1 + (i * res_degree), res_degree)

        cell_area = cell_width * cell_length

        haversine_grid = np.append(haversine_grid, cell_area)

    haversine_grid = np.expand_dims(haversine_grid, axis=1)
    haversine_grid = np.repeat(haversine_grid, lat_cells, axis=1)

    # Write Haversine Grid to .tif using rasterio, copy profile from file2copy.
    with rasterio.open(file2copy) as src:  # open tif file
        profile = src.profile  # aqcuire all metadata
        profile.update(dtype=rasterio.float64, compress='lzw', nodata=0)  # update metadata

    with rasterio.open(output_filename, 'w', **profile) as dst:  # open output file
        dst.write(haversine_grid.astype(rasterio.float64), 1)  # write array to geotiff


create_haversine_grid('input.tif', 'output_haversine.tif')
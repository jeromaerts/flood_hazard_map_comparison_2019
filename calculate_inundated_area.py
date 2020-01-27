"""
Author: Jerom Aerts
Contact: j.p.m.aerts@tudelft.nl

Description:
Calculate inundated area of flood hazard map after data homogenization

This script requires the following two components in order to work:
- Haversine grid, see create_haversine_grid.py
- binary flood hazard map, see data_homogenization.py
"""

import os
import numpy as np
import rasterio

def inundated_area(floodmap, haversine_grid):
    
    # Load floodmap and haversine grid
    src_A = rasterio.open(floodmap)    
    profile = src_A.meta.copy()
    src_B = rasterio.open(haversine_grid)

    # Create empty array for filling
    inundated_area = np.zeros([1,73800])
    
    # Loop through arrays
    i = 0
    for ji, window in src_A.block_windows(1):
        i += 1

        affine = rasterio.windows.transform(window, src_A.transform)
        height, width = rasterio.windows.shape(window)
        bbox = rasterio.windows.bounds(window, src_A.transform)
        
        profile.update({
            'height': height,
            'width': width,
            'affine': affine})
            
        array_A = src_A.read(1, window=window)
        array_B = src_B.read(1, window=window)

        # Multiply binary array with haversine array to retrieve inundated area
        array_combined = array_A * array_B
        array_combined = np.sum(array_combined)
        inundated_area = np.append(inundated_area, array_combined)
        inundated_area = np.sum(inundated_area,0)
        
    return inundated_area
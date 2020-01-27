"""
Author: Jerom Aerts
Contact: j.p.m.aerts@tudelft.nl

Description:
Calculate exposed GDP of flood hazard map after data homogenization

This script requires the following two components in order to work:
- Gridded GDP layer, see create_haversine_grid.py
- Binary flood hazard map, see data_homogenization.py
"""

import os
import numpy as np
import rasterio

def exposed_GDP(floodmap, GDP_layer):
    
    # Load floodmap and haversine grid
    src_A = rasterio.open(floodmap)    
    profile = src_A.meta.copy()
    src_B = rasterio.open(GDP_layer)

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

        # Multiply binary array with haversine array to retrieve exposed GDP
        array_combined = array_A * array_B
        array_combined = np.sum(array_combined)
        exposed_GDP = np.append(exposed_GDP, array_combined)
        exposed_GDP = np.sum(exposed_GDP,0)
        
    return exposed_GDP
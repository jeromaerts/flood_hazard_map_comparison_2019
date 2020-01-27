"""
Author: Jerom Aerts
Contact: j.p.m.aerts@tudelft.nl

Description:
Example of MAI calculation for the RP100 scenario fluvial undefended flood hazard maps.
The same script can be adjusted different RPs, flood types or flood protection scenarios.

This script requires the following component in order to work:
- Rastersum grid, see create_rastersum_example.py
- haversine grid, see create_haversine_grid.py
"""

import os
import numpy as np
import time
import rasterio

# Set rastersum and haversine filenames
raster = "rastersum_RP100.tif" 
haversine = "haversine_grid.tif"

def inundated_area(aggr_cat):
    # Function calculates the inundated area using a haversine grid for each aggregate category
    src_A = rasterio.open(raster)    
    profile = src_A.meta.copy()
    src_B = rasterio.open(haversine)
    inundated_area = np.zeros([1,73800])
    
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
            
        array_A = src_A.read(window=window)
        array_B = src_B.read(window=window)
        
        if array_A.shape[0] == 1: #Reshape 3 dimensional array to 2 dimensional array
            array_A = array_A.reshape(array_A.shape[1:]) #Reshape 3 dimensional array to 2 dimensional array
        if array_B.shape[0] == 1: #Reshape 3 dimensional array to 2 dimensional array
            array_B = array_B.reshape(array_B.shape[1:]) #Reshape 3 dimensional array to 2 dimensional array
            
        array_A = np.where(array_A == aggr_cat,1,0) #extract binary values
        
        # Calculate inundated area in km2 for each aggregate_category
        array_combined = array_A * array_B
        array_combined = np.sum(array_combined)
        inundated_area = np.append(inundated_area, array_combined)
        inundated_area = np.sum(inundated_area,0)
        
    return inundated_area

# Calculate inundated area for each aggregate category
inun_1 = inundated_area(1)
inun_2 = inundated_area(2)
inun_3 = inundated_area(3)
inun_4 = inundated_area(4)
inun_5 = inundated_area(5)
inun_6 = inundated_area(6)

# Calculate total inundated area
area_total = inun_1+inun_2+inun_3+inun_4+inun_5+inun_6

a2 = (2/6)*inun_2
a3 = (3/6)*inun_3 
a4 = (4/6)*inun_4 
a5 = (5/6)*inun_5 
a6 = (6/6)*inun_6

# Calculate MAI
MAI = (a2+a3+a4+a5+a6)/area_total
"""
Author: Jerom Aerts
Contact: j.p.m.aerts@tudelft.nl

Description:
Example of the creation of a rastersum grid (the aggregate of flood hazard maps with a similar return period (RP).
The same script can be adjusted different RPs, flood types or flood protection scenarios.

This script requires the following component in order to work:
- Binary flood hazard maps with the same return period.
"""

import rasterio
from rasterio import features
from rasterio.transform import Affine
from rasterio.windows import Window
import numpy as np
import time
import os

if __name__ == '__main__':

    # Load all flood hazard maps that are going to be aggregated
    raster_A = "RP100_map_A.tif"
    raster_B = "RP100_map_B.tif"
    raster_C = "RP100_map_C.tif"
    raster_D = "RP100_map_D.tif"
    raster_E = "RP100_map_E.tif"
    raster_F = "RP100_map_F.tif"
    
    raster_out = "rastersum_RP100.tif"
    
    src_A = rasterio.open(raster_A)
    src_B = rasterio.open(raster_B)
    src_C = rasterio.open(raster_C)
    src_D = rasterio.open(raster_D)
    src_E = rasterio.open(raster_E)
    src_F = rasterio.open(raster_F)
    
    profile = src_A.meta.copy()
    profile.update(dtype=rasterio.uint8, compress='lzw', nodata=0) #update metadata
    nodata = src_A.nodata
    
    # Loop through rasters
    with rasterio.open(raster_out, 'w', **profile) as dst:
        # per block
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
            array_C = src_C.read(window=window)
            array_D = src_D.read(window=window)
            array_E = src_E.read(window=window)
            array_F = src_F.read(window=window)
            
            # Aggregate rasters
            data_wdw = np.empty_like(array_A, dtype='b')
            data_wdw = np.append(array_A, array_B, 0,)
            data_wdw = np.append(data_wdw, array_C, 0)
            data_wdw = np.append(data_wdw, array_D, 0)
            data_wdw = np.append(data_wdw, array_E, 0)
            data_wdw = np.append(data_wdw, array_F, 0)
            data_wdw = np.sum(data_wdw, 0)
            
            # Write output
            dst.write(data_wdw.astype(rasterio.uint8), window=window, indexes=1)
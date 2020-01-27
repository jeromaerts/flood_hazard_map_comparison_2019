"""
Author: Jerom Aerts
Contact: j.p.m.aerts@tudelft.nl

Description:
Example of how to create defended flood hazard maps by removing protected areas that are specifies in a flood protection layer.
The same script can be adjusted different RPs, flood types or flood protection scenarios.

This script requires the following component in order to work:
- Flood hazard maps
- Flood protection layer
"""

import rasterio
from rasterio import features
from rasterio.transform import Affine
from rasterio.windows import Window
import numpy as np
import time
import os


# This is an example for a flood hazard map with a 20 year return period (RP20)
# The flood protection layers are binary layers with 0 for protected areas and 1 for unprotected areas
protection_RP10 = 'protection_RP10.tif'
protection_RP20 = 'protection_RP20.tif'

for f in os.listdir(WorkingFolder):   # loop through for each file in the folder
    fName, fExt = os.path.splitext(f) # break up file name and extension
    if fExt.upper() == '.TIF': #only use tif files
        
        filename = fName+fExt # filename for use in subprocess
        filename2 = fName+"_protected"+fExt
    
        src_A = rasterio.open(filename)
        src_B = rasterio.open(protection_RP10)
        src_C = rasterio.open(protection_RP20)
        
        profile = src_A.meta.copy()
        profile.update(dtype=rasterio.uint8, compress='lzw', nodata=0) #update metadata

        with rasterio.open(filename2, 'w', **profile) as dst:
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
            
                array_A = src_A.read(1,window=window)
                array_B = src_B.read(1,window=window)
                array_C = src_C.read(1,window=window)
                
                # remove protected areas by multiplying the binary flood hazard map with the inverse binary flood protection layer
                array_A = array_A*array_B
                array_A = array_A*array_C
                
                print(i)
                # write output
                dst.write(array_A.astype(rasterio.uint8), window=window, indexes=1)
        

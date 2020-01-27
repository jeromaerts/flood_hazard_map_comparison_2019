"""
Author: Jerom Aerts
Contact: j.p.m.aerts@tudelft.nl

Description:
Data homogenization script for China flood hazard map comparison

This script requires the following three components in order to work:
- Raster at required resolution of case study area
- Mask created by rasterizing a shapefile (www.gadm.org) of case study extent
- Mask of waterbodies which will be removed (doi:10.1038/nature20584)
"""

import os
import sys
import subprocess
import numpy as np
import rasterio
import fiona

working_directory = '' # Set to working directory

for f in os.listdir(working_directory): # loop through for each file in the folder
    fName, fExt = os.path.splitext(f)   # break up file name and extension
    if fExt.upper() == '.TIF':          # only use tif files

        # Set filenames for each processing step
        filename  = fName + fExt 
        filename2 = fName + '_clip'+ fExt 
        filename3 = fName + '_resample' + fExt
        filename4 = fName + '_binary' + fExt
        filename5 = fName + '_burned'+ fExt 

        # Step 1: Clip files to smaller extent to avoid large filesizes
        subprocess.call("gdalwarp -multi -wm 500 -te 73.5 18.0 135.0 54.0 %s %s"%(filename, filename2) , shell=True)

        # Step 2: Resample the clipped file to the required resolution (set to nearest neighbour, change to bilinear for GDP layers)
        subprocess.call("rio warp  %s %s --like C:\Folder\china_3arcseconds.tif --co blockxsize=400 --co blockysize=400 --resampling nearest"%(filename2, filename3) , shell=True)

        # Step 3: Convert resampled files to files with binary format (values larger than 0 meters of water depth are considered to be flooded and set to 1),
        #       : Multiply result with mask layer

        src_A = rasterio.open(filename3)
        src_B = rasterio.open(mask_layer)
        
        profile = src_A.meta.copy()
        profile.update(dtype=rasterio.uint8, compress='lzw', nodata=0) #update metadata
        nodata = src_A.nodata

        with rasterio.open(filename4, 'w', **profile) as dst:
            # per block
            i = 0
            for ji, window in src_A.block_windows(1) and src_B.block_windows(1):
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
                print(i)

                array_A = np.where(array_A > 0,1,0) #extract binary values

                array_A = array_A * array_B 
            
                dst.write(array_A.astype(rasterio.uint8), window=window, indexes=1)

                start_burn = time.time()

        # Step 4: Multiply result with mask of neutral water bodies, see methods chapter for further details       
        src_A = rasterio.open(filename4)
        src_B = rasterio.open(waterbodies)
        
        profile = src_A.meta.copy()
        profile.update(dtype=rasterio.uint8, compress='lzw', nodata=0) #update metadata
        nodata = src_A.nodata
        
        with rasterio.open(filename5, 'w', **profile) as dst:
            # per block
            i = 0
            for ji, window in src_A.block_windows(1) and src_B.block_windows(1):
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
                print(i)

                array_A = array_A * array_B #mask layer
            
                dst.write(array_A.astype(rasterio.uint8), window=window, indexes=1)
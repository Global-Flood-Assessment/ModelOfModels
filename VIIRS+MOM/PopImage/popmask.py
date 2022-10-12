"""
    popmask.py
        -- generate the population mask for a wastershed
"""

import sys, os, csv, json
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import numpy as np

def watersheds_gdb_reader():
    """reader watersheds gdb into geopandas"""

    watersheds_gdb = "../../VIIRS_Processing/Watershed_pfaf_id.shp"
    watersheds = gpd.read_file(watersheds_gdb)
    watersheds.set_index("pfaf_id",inplace=True)

    return watersheds

def jsonmask(wdata, apfaf_id):

    amask = json.loads(gpd.GeoSeries([wdata.loc[apfaf_id,'geometry']]).to_json())
    
    return amask



# raster mask function
def clipbymask(tiffimage, mask_json,clippedimage):
    """ clip a [tiffimage] by [mask_josn], saved as [clippedimage]"""
    
    with rasterio.open(tiffimage) as src:
        try:
            out_image, out_transform = mask(src, [mask_json['features'][0]['geometry']], crop=True)
            out_meta = src.meta.copy()
        except ValueError as e:
            #'Input shapes do not overlap raster.'
            src = None
            area=0
            # return empty dataframe
            return area
    out_meta.update({"height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform},
                    compress='lzw')
    with rasterio.open(clippedimage, "w", **out_meta) as dest:
        dest.write(out_image)

    src = rasterio.open(clippedimage)
    data = src.read(1)
    print(clippedimage, "total population count")
    print(int(np.sum(data,where=(data != src.nodata))))
    src.close()



def main():
    pfaf_id = 732572
    wdata = watersheds_gdb_reader()
    the_mask = jsonmask(wdata,pfaf_id)
    #save the mask json
    with open(f'{pfaf_id}.geojson', "w") as outfile:
        outfile.write(json.dumps(the_mask))

    bbox = the_mask['bbox']
    # "bbox": [-81.43390062099994, 25.507766046000057, -80.18333333399997, 26.646362983000046]}
    x1,y1,x2,y2 = bbox
    #-projwin ulx uly lrx lry 
    projwin = " ".join(map(str,[x1-0.15,y2+0.15,x2+0.15,y1-0.15]))
    # generate tiff image
    vtkfile = os.path.expanduser('~/Documents/MoM_PoP/pop.vrt')
    temptiff = os.path.join(os.getcwd(),f'{pfaf_id}.tiff')
    gdalcmd = f"gdal_translate -of GTiff -projwin {projwin} {vtkfile} {temptiff}"
    os.system(gdalcmd)

    mask_tiff = f'{pfaf_id}_pop.tiff'
    clipbymask(temptiff,the_mask,mask_tiff)

    # delete temp tiff
    os.remove(temptiff)

if __name__ == "__main__":
    main()
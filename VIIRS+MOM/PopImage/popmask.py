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


def countpop(popimage):
    """count the total poplation inside an image"""

    src = rasterio.open(popimage)
    data = src.read(1)
    total_pop = int(np.sum(data,where=(data != src.nodata)))
    src.close()

    return total_pop

def main():
    
    pfaf_id = 732572
    wdata = watersheds_gdb_reader()
    pfaf_id_list = wdata.index.values.tolist()
    totalw = len(pfaf_id_list)
    counter = 1
    pop_count = os.path.join(os.getcwd(),'popcount.csv')
    with open(pop_count,'w') as csvfile:
        csvfile.write('pfaf_id,totalpop\n')

    for pfaf_id in pfaf_id_list:
        print(f'processing {pfaf_id}, {counter} of {totalw}')

        # check if it is processed first
        mask_tiff = os.path.join(os.getcwd(),'poptiff',f'{pfaf_id}_pop.tiff')
        if os.path.exists(mask_tiff):
            counter += 1
            continue

        the_mask = jsonmask(wdata,pfaf_id)
        #save the mask json
        maskjson = os.path.join(os.getcwd(),'maskgeojson',f'{pfaf_id}.geojson')        
        with open(maskjson, "w") as outfile:
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

        clipbymask(temptiff,the_mask,mask_tiff)

        # delete temp tiff
        os.remove(temptiff)
        total_pop = countpop(mask_tiff)
        with open(pop_count,'a') as csvfile:
            csvfile.write(f'{pfaf_id},{total_pop}\n')

        counter += 1

if __name__ == "__main__":
    main()
"""
    DFO_process.py
        -- Process DFO data
"""
import sys, os, csv, json, shutil
from datetime import datetime
import numpy as np
import pandas as pd
from osgeo import gdal
import geopandas
import pandas as pd
import rasterio
from rasterio.mask import mask
from rasterio import Affine # or from affine import Affine
from shapely.geometry import Point

from progressbar import progress


def get_date(foldername):
    """ get the real date"""
    
    #allData/61/MCDWD_L3_NRT/2021/021

    year,day_num = foldername.split("/")[-2:]
    res = datetime.strptime(year + "-" + day_num, "%Y-%j").strftime("%Y%m%d")

    return res

def watersheds_gdb_reader():
    """reader watersheds gdb into geopandas"""

    #watersheds_gdb = 'WRIWatersheds.gdb'
    # watersheds_gdb = 'AQID_Watwershed_Jan2020/AQID_Watwershed_Jan2020.shp'
    # watersheds = geopandas.read_file(watersheds_gdb)
    # watersheds.set_index("aqid",inplace=True)
    
    #pfaf_id, areakm2
    if not 'basepath' in vars():
        basepath = os.path.dirname(os.path.abspath(__file__))
    watersheds_gdb = basepath + '/Watersheds_032020/wastershed_prj_latlon.shp'
    watersheds = geopandas.read_file(watersheds_gdb)
    watersheds.rename(columns={"pfaf_id": "aqid"},inplace=True)
    watersheds.set_index("aqid",inplace=True)

    return watersheds

def DFO_extract_by_mask(vrt_file,mask_json):
    """extract DFO data for a given watershed"""

    #print(vrt_file)
    #print(mask_json['features'][0]['geometry'])
    with rasterio.open(vrt_file) as src:
        try:
            out_image, out_transform = mask(src, [mask_json['features'][0]['geometry']], crop=True)
        except ValueError as e:
            #'Input shapes do not overlap raster.'
            #print(e)
            src = None
            # return empty dataframe
            return 0

    # extract data
    no_data = src.nodata
    # extract the values of the masked array
    #print(out_image)
    data = out_image[0]
    point_count = np.count_nonzero(data == 3)
    src = None

    # total area
    d = point_count * 0.25 * 0.25
    
    return d

def DFO_extract_by_watershed(vtk_file,aqid_list,gen_plot = False):
    """extract and summary"""

    watersheds = watersheds_gdb_reader()
    if len(aqid_list) == 0:
        # take the list from watersheds gdb
        #aqid is the index column
        aqid_list = watersheds.index.tolist()
    
    # setup output file
    # get header from vtk file
    # Flood_2-Day_250m.vrt
    headerprefix = os.path.basename(vtk_file).split("_")[1]
    if ("_CS_" in vtk_file):
        headerprefix = "1-Day_CS"

    headers_list = ["pfaf_id", headerprefix + "_TotalArea_km2",headerprefix + "_perc_Area"]
    summary_file = os.path.basename(vtk_file)[:-4]+ ".csv"
    if not os.path.exists(summary_file):
        with open(summary_file,'w') as f:
            writer = csv.writer(f)
            writer.writerow(headers_list)  
    else:
        # already processed, 
        return 

    count = 0
    with open(summary_file, 'a') as f:
        writer = csv.writer(f)

        for the_aqid in aqid_list:
            count += 1
            #print(the_aqid, count, " out of ", len(aqid_list))
            progress(count,  len(aqid_list), status='aqid')
            # extract mask
            test_json = json.loads(geopandas.GeoSeries([watersheds.loc[the_aqid,'geometry']]).to_json())
            # plot check
            dfoarea = DFO_extract_by_mask(vtk_file, test_json)

            DFO_TotalArea = dfoarea
            DFO_Area_percent = DFO_TotalArea/watersheds.loc[the_aqid]['areakm2']*100

            results_list = [the_aqid,"{:.3f}".format(DFO_TotalArea),"{:.3f}".format(DFO_Area_percent)]
            writer.writerow(results_list)
        
    return summary_file
     

def DFO_process(hdffolder,outputfolder,datestr=''):
    """ process DFO data 
    
        folder structure
        allData/61/MCDWD_L3_NRT/2021/021
            |-Flood 1-Day 250m
            |-Flood 1-Day CS 250m
            |-Flood 2-Day 250m
            |-Flood 3-Day 250m         
            Flood_3-Day_250m.vrt
            Flood_2-Day_250m.vrt
            Flood_1-Day_CS_250m.vrt
            Flood_1-Day_250m.vrt
    """
    
    if "~" in hdffolder:
        hdffolder = os.path.expanduser(hdffolder)
    if "~" in outputfolder:
        outputfolder = os.path.expanduser(outputfolder)

    # switch working directory
    os.chdir(hdffolder)

    floodlayer = ["Flood 1-Day 250m","Flood 1-Day CS 250m","Flood 2-Day 250m","Flood 3-Day 250m"]  

    # create sub folder if necessary
    for flood in floodlayer:
        subfolder = flood.replace(" ","_")
        if not os.path.exists(subfolder):
            os.mkdir(subfolder)

    # MCDWD_L3_NRT.A2021022.h06v04.061.hdf
    #HDF4_EOS:EOS_GRID:"MCDWD_L3_NRT.A2021022.h06v04.061.hdf":Grid_Water_Composite:"Flood 1-Day 250m"
    #HDF4_EOS:EOS_GRID:"MCDWD_L3_NRT.A2021022.h06v04.061.hdf":Grid_Water_Composite:"Flood 1-Day CS 250m"
    #HDF4_EOS:EOS_GRID:"MCDWD_L3_NRT.A2021022.h06v04.061.hdf":Grid_Water_Composite:"Flood 2-Day 250m"
    #HDF4_EOS:EOS_GRID:"MCDWD_L3_NRT.A2021022.h06v04.061.hdf":Grid_Water_Composite:"Flood 3-Day 250m"
    #HDF4_EOS:EOS_GRID:"{HDF}":Grid_Water_Composite:"{floodLAYER}"

    # scan hdf files
    hdffiles = []
    for entry in os.listdir():
        if entry[-4:] != ".hdf":
            continue    
        HDF = entry
        hdffiles.append(HDF)
    
    # one step one image operation
    vrt_list = []
    for flood in floodlayer:
        subfolder = flood.replace(" ","_")
        # geotiff convert
        for HDF in hdffiles:
            nameprefix = "_".join(HDF.split(".")[1:3])
            inputlayer = f'HDF4_EOS:EOS_GRID:"{HDF}":Grid_Water_Composite:"{flood}"'
            tiff = nameprefix + "_" + subfolder
            outputtiff = subfolder + os.path.sep + tiff + ".tiff"
            if not os.path.exists(outputtiff):
                # gdal cmd
                gdalcmd = f'gdal_translate -of GTiff -co Tiled=Yes {inputlayer} {outputtiff}'
                # convert geotiff
                os.system(gdalcmd)
        # build vrt
        gdalcmd = f'gdalbuildvrt {subfolder}.vrt {subfolder}/*.tiff'
        #print(gdalcmd)
        os.system(gdalcmd)

        vrt = f'{subfolder}.vrt'
        vrt_list.append(vrt)
        # extract flood data
        DFO_extract_by_watershed(vrt,[])

        # build geotiff
        if "3-Day" in vrt:
            tiff =  outputfolder + os.path.sep + "DFO_image/DFO_" + datestr + "_" + vrt.replace(".vrt",".tiff")
            # gdal_translate -co TILED=YES -co COMPRESS=PACKBITS -of GTiff Flood_1-Day_250m.vrt Flood_1-Day_250m.tiff
            # gdaladdo -r average Flood_1-Day_250m.tiff 2 4 8 16 32
            gdalcmd = f'gdal_translate -co TILED=YES -co COMPRESS=PACKBITS -of GTiff {vrt} {tiff}'
            os.system(gdalcmd)
            # build overview
            gdalcmd = f'gdaladdo -r average {tiff} 2 4 8 16 32'
            os.system(gdalcmd)
        
        # delete tiff folder
        if os.path.exists(subfolder):
            shutil.rmtree(subfolder)   

    
    # merge flood data into one file
    csv_list = []
    for vrt in vrt_list:
        csvfile = vrt.replace(".vrt",".csv")
        pdc = pd.read_csv(csvfile)
        csv_list.append(pdc)
    
    merged = csv_list[0].merge(csv_list[1], on='pfaf_id')
    merged = merged.merge(csv_list[2], on='pfaf_id')
    merged = merged.merge(csv_list[3], on='pfaf_id')

    # get the date
    if datestr=='':
        datestr = get_date(hdffolder)
    # save output
    summary_csv = outputfolder + os.path.sep + "DFO_summary/DFO_" + datestr + ".csv"
    merged.to_csv(summary_csv)

    # zip the original data folder
    # just store file  
    #zipped = outputfolder + os.path.sep + "data/DFO_" + datestr + ".zip"
    #zipcmd = f'zip -r -0 {zipped} ./*'
    #os.system(zipcmd)

def debug():
    """ part for debug """
    # wkdir = "allData/61/MCDWD_L3_NRT/2021/021"
    # vrt_file = "Flood_1-Day_CS_250m.vrt"
    # aqids_test=[771990]
    # DFO_extract_by_watershed(wkdir + "/" + vrt_file,[])

    datestr = get_date('allData/61/MCDWD_L3_NRT/2021/051')
    print(datestr)

    sys.exit()

def main():

    #debug()
    global basepath
    basepath = os.path.dirname(os.path.abspath(__file__))

    data_list = ["222"]
    for entry in data_list:
        testdata = "~/Projects/ModelOfModels/data/rawdata/dfo/" + entry
        outputfolder = "~/Projects/ModelOfModels/data/cron_data/DFO"
        DFO_process(testdata,outputfolder)
        # switch back to basepath
        os.chdir(basepath)

if __name__ == "__main__":
    main()
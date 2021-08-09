"""
    HWRF_Rainfall_cron.py
        -- cron job script for HWRF data
"""

import sys, os
import yaml
import requests
from bs4 import BeautifulSoup
import logging
import subprocess
from osgeo import gdal
import pandas as pd
import geopandas as gpd
import csv
import json
import rasterio
from rasterio.mask import mask
import numpy as np
from rasterio import Affine
import math
from shapely.geometry import Point
import shutil
import zipfile

def load_config(onetime=''):
    """load configuration file """
    with open("HWRF_config.yml", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    global hosturl
    hosturl = cfg['HWRF']['host']

    folderprefix = cfg['datalocation']['folderprefix']
    folderprefix = os.path.abspath(folderprefix) + os.path.sep
    global HWRFsummary
    HWRFsummary = folderprefix + cfg['datalocation']['HWRFsummary'] + os.path.sep
    global HWRFimage 
    HWRFimage = folderprefix + cfg['datalocation']['HWRFimage'] + os.path.sep
    global HWRFoutput
    HWRFoutput = folderprefix + cfg['datalocation']['HWRFoutput']
    global HWRFraw 
    HWRFraw = folderprefix + cfg['datalocation']['HWRFraw'] + os.path.sep
    global flood_HWRF
    flood_HWRF= folderprefix + cfg['datalocation']['flood_HWRF'] + os.path.sep
    global flooddata
    flooddata= folderprefix + cfg['datalocation']['flooddata'] + os.path.sep
    
    # set up logging file
    logging.basicConfig(filename = cfg['datalocation']['loggingfile'], format='%(asctime)s %(message)s', level=logging.INFO)

def check_status(adate):
    """ check if a give date is processed"""

    processed_list = os.listdir(HWRFsummary)
    processed = any(adate in x for x in processed_list)
    
    return processed

def generate_procesing_list():
    """ generate the processing list"""
    reqs = requests.get(hosturl)
    soup = BeautifulSoup(reqs.text,"html.parser")
    
    datelist = {}
    for link in soup.find_all('a'):
        fstr = link.string
        if (fstr[:5] == 'hwrf.'):
            a_entry = fstr.split('.')[1]
            a_entry = a_entry.replace("/","")
            if check_status(a_entry):
                continue
            datelist[a_entry] = hosturl + fstr
    
    return datelist

def HWRF_download(hwrfurl):
    """ download rainfall data"""
    reqs = requests.get(hwrfurl)
    soup = BeautifulSoup(reqs.text,"html.parser")

    ascii_list = []
    for link in soup.find_all('a'):
        fstr = link.string
        if "rainfall.ascii" in fstr:
            if not os.path.exists(HWRFraw + fstr):
                wgetcmd = "wget " + hwrfurl + fstr + " -P " + HWRFraw
                subprocess.call(wgetcmd, shell=True)
            ascii_list.append(fstr)
    
    return ascii_list

def process_rain(adate,TC_Rain):
    """process rainfall data"""

    ## VRT template to read the csv
    vrt_template="""<OGRVRTDataSource>
        <OGRVRTLayer name='{}'>
            <SrcDataSource>{}</SrcDataSource>
            <GeometryType>wkbPoint</GeometryType>
            <GeometryField encoding="PointFromColumns" x="lon" y="lat" z="Z"/>
        </OGRVRTLayer>
    </OGRVRTDataSource>"""

    ## Read each text file and create the separate tiff file
    for i in TC_Rain:
        with open(i,'r') as f:
            variable=csv.reader(f, delimiter=' ') 
            row_count=1 
            for row in variable:
                if row_count == 1: 
                    while ('' in row):
                        row.remove('')
                    XLC=float(row[0]) 
                    XRC=float(row[1]) 
                    YBC=float(row[2]) 
                    YTC=float(row[3])
                    res=float(row[4])
                    nrows=float(row[5])
                    ncol=float(row[6])
                    row_count = row_count + 1
        df = (pd.read_table(i, skiprows=1, delim_whitespace=True, names=('lat', 'lon', 'Z'))).fillna(-999)
        df.sort_values(by=["lat","lon"], ascending=[False, True])
        df=df[['lon','lat','Z']]
        df = df[df.lon >= XLC]
        df = df[df.lon <= XRC]
        df = df[df.lat >= YBC]
        df = df[df.lat <= YTC]
        df = df[df.Z > 0]
        df.to_csv(i.replace(".ascii",".csv"),index=False, sep=" ")
        with open(i.replace(".ascii",".vrt"),"w") as g:
            g.write(vrt_template.format(i.replace(".ascii",""),i.replace(".ascii",".csv")))
        g.close()
        r=gdal.Rasterize(i.replace(".ascii",".tiff"),i.replace(".ascii",".vrt"),outputSRS="EPSG:4326",xRes=res, yRes=res,attribute="Z", noData=-999)
        r=None
        os.remove(i.replace(".ascii",".csv"))

    ##merge all  tiffs file als
    # nd delete the individual tiff, vrt and ascii file 

    TC_Rain_tiff=[]
    for i in TC_Rain:
        TC_Rain_tiff.append(i.replace(".ascii",".tiff"))

    filename="hwrf."+ adate +"rainfall.vrt"
    raintiff = filename.replace(".vrt",".tiff")
    vrt = gdal.BuildVRT(filename, TC_Rain_tiff)
    gdal.Translate(raintiff, vrt)
    vrt=None
    # no need
    #gdalcmd = "gdal_translate -of GTiff " + filename + " " + raintiff
    #subprocess.call(gdalcmd, shell=True)

    # create a zipfile
    zip_file="hwrf."+ adate +"rainfall.zip"
    with zipfile.ZipFile(zip_file, 'w',zipfile.ZIP_DEFLATED) as zipObj:
        for i in TC_Rain_tiff:
            asfile = i.replace(".tiff",".ascii")
            zipObj.write(asfile)
    for i in TC_Rain_tiff:
        os.remove(i)
        os.remove(i.replace(".tiff",".ascii"))
        os.remove(i.replace(".tiff",".vrt"))

    return raintiff

def HWRF_extract_by_mask(mask_json,tiff):
    """extract by each watershed"""

    with rasterio.open(tiff) as src:
        try:
            out_image, out_transform = mask(src, [mask_json['features'][0]['geometry']], crop=True)
        except ValueError as e:
            #'Input shapes do not overlap raster.'
            #print(e)
            src = None
            # return empty dataframe
            return pd.DataFrame()

    # extract data
    no_data = src.nodata
    # extract the values of the masked array
    #print(out_image)
    data = out_image[0]
    # extract the row, columns of the valid values
    row, col = np.where(data != no_data) 
    point_value = np.extract(data != no_data, data)
    if (len(point_value)== 0):
        src = None
        # return empty dataframe
        return pd.DataFrame()

    T1 = out_transform * Affine.translation(0.5, 0.5) # reference the pixel centre
    rc2xy = lambda r, c: (c, r) * T1  
    px,py=src.res
    #print (px,py)
    pixel_area_km2 = lambda lon, lat: 111.111*111.111*math.cos(lat*0.01745)*px*py 
    d = gpd.GeoDataFrame({'col':col,'row':row,'intensity':point_value})
    # coordinate transformation
    d['lon'] = d.apply(lambda row: rc2xy(row.row,row.col)[0], axis=1)
    d['lat'] = d.apply(lambda row: rc2xy(row.row,row.col)[1], axis=1)
    d['area'] = d.apply(lambda row: pixel_area_km2(row.lon,row.lat), axis=1)
    
    # geometry 
    d['geometry'] =d.apply(lambda row: Point(row['lon'], row['lat']), axis=1)
    # first 2 points
    src = None
    return d

def HWRF_extract_by_watershed(raintiff):
    """extract flood info by watershed"""

    ## zonal analysis using merged tiff and watersheds 
    #if not 'basepath' in vars():
    #    basepath = os.path.dirname(os.path.abspath(__file__))
    watersheds_gdb = basepath + '/Watershed_pfaf_id.shp'
    watersheds = gpd.read_file(watersheds_gdb)
    watersheds.set_index("pfaf_id",inplace=True) 
    pfafid_list = watersheds.index.tolist()

    headers_list = ["pfaf_id","Rain_TotalArea_km","perc_Area","MeanRain","MaxRain",]
    output_csv = raintiff.replace(".tiff",".csv")
    with open(output_csv,'w') as f:
        writer = csv.writer(f)
        writer.writerow(headers_list)  
    has_data = False
    with open(output_csv, 'a') as f:
        writer = csv.writer(f)
        for the_pfafid in pfafid_list:
            test_json = json.loads(gpd.GeoSeries([watersheds.loc[the_pfafid,'geometry']]).to_json())
            if test_json['features'][0]['geometry'] == None:
                continue
            data_points = HWRF_extract_by_mask(test_json, raintiff)
                # write summary to a csv file
            if (not data_points.empty):
                HWRF_TotalArea_km = data_points['area'].sum()                
                HWRF_perc_Area = HWRF_TotalArea_km/watersheds.loc[the_pfafid]['area_km2']*100
                HWRF_MeanRain = data_points['intensity'].mean()
                HWRF_MaxRain = data_points['intensity'].max() 
                results_list = [the_pfafid,HWRF_TotalArea_km,HWRF_perc_Area,HWRF_MeanRain,HWRF_MaxRain]
                writer.writerow(results_list)
                has_data=True
    # has_data, move file to the right locaition
    # no_data, delete all the file
    if has_data:
        shutil.move(output_csv,HWRFsummary)
        shutil.move(raintiff,HWRFimage)
        os.remove(raintiff.replace(".tiff",".vrt"))
    else:
        os.remove(raintiff)
        os.remove(output_csv)
        os.remove(raintiff.replace(".tiff",".vrt"))

    return [output_csv, has_data]

def HWRF_cron():
    """ main cron script"""
    
    global basepath
    basepath = os.path.dirname(os.path.abspath(__file__))

    load_config()

    # get date list
    datelist = generate_procesing_list()

    if len(datelist) == 0:
        logging.info("no new data to process!")
        sys.exit(0)
    
    # download - process ascii
    for key in datelist:
        logging.info("check: " + key)
        a_list = HWRF_download(datelist[key])
        #a_list=['haha']
        if len(a_list) == 0:
            logging.info("no rainfall data " + key)
            continue
        #switch directory to HWRFraw
        os.chdir(HWRFraw)
        logging.info("processing " + key)
        newtiff = process_rain(key,a_list)
        #newtiff = "hwrf."+ key +"rainfall.tiff"
        logging.info("processing " + newtiff)
        [hwrfcsv,dataflag] = HWRF_extract_by_watershed(newtiff)
        if not dataflag:
            logging.info("no data: " + hwrfcsv)
            continue
        logging.info("hwrf summary: " + hwrfcsv)
        
def main():
    HWRF_cron()

if __name__ == "__main__":
    main()
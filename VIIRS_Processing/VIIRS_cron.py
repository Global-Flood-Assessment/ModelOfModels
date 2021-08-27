"""
    VIIRS_cron.py
        -- process VIIRS data
        -- https://www.ssec.wisc.edu/flood-map-demo/ftp-link

        output:
        -- VIIRS_Flood_yyyymmdd.csv at VIIRS_summary
        -- VIIRS_1day_compositeyyyymmdd_flood.tiff at VIIRS_image
        -- VIIRS_5day_compositeyyyymmdd_flood.tiff at VIIRS_image
"""

import sys, os, csv, json
import yaml
import requests
import logging
import datetime
from osgeo import gdal
import rasterio
from rasterio.mask import mask
import numpy as np
import pandas as pd
import geopandas as gpd


def load_config(onetime=''):
    """load configuration file """
    with open("VIIRS_config.yml", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    global hosturl
    hosturl = cfg['VIIRS']['host']

    folderprefix = cfg['datalocation']['folderprefix']
    folderprefix = os.path.abspath(folderprefix) + os.path.sep
    global VIIRSsummary
    VIIRSsummary = folderprefix + cfg['datalocation']['VIIRSsummary'] + os.path.sep
    global VIIRSimage 
    VIIRSimage = folderprefix + cfg['datalocation']['VIIRSimage'] + os.path.sep
    global VIIRSoutput
    VIIRSoutput = folderprefix + cfg['datalocation']['VIIRSoutput']
    global VIIRSraw 
    VIIRSraw = folderprefix + cfg['datalocation']['VIIRSraw'] + os.path.sep
    global flood_VIIRS
    flood_VIIRS= folderprefix + cfg['datalocation']['flood_VIIRS'] + os.path.sep
    global flooddata
    flooddata= folderprefix + cfg['datalocation']['flooddata'] + os.path.sep
    
    # set up logging file
    logging.basicConfig(filename = cfg['datalocation']['loggingfile'], format='%(asctime)s %(message)s', level=logging.INFO)

def check_status(adate):
    """ check if a give date is processed"""

    summaryfile = VIIRSsummary + "VIIRS_Flood_{}.csv".format(adate)
    if os.path.exists(summaryfile):
        processed = True
    else:
        processed = False

    return processed

def generate_adate():
    """ generate 1 day delay date"""

    previous_date = datetime.datetime.today() - datetime.timedelta(days=1)

    adate_str = previous_date.strftime("%Y%m%d")
    
    return adate_str

def check_data_online(adate):
    """ check data is online for a given date"""
    # total 136 AOIs
    # 5-day composite
    # https://floodlight.ssec.wisc.edu/composite/RIVER-FLDglobal-composite_*_000900.part*.tif
    # 1-day composite
    # https://floodlight.ssec.wisc.edu/composite/RIVER-FLDglobal-composite1_*_000000.part*.tif
    
    testurl = 'https://floodlight.ssec.wisc.edu/composite/RIVER-FLDglobal-composite_{}_000000.part001.tif'
    testurl = testurl.format(adate)
    r = requests.head(testurl)
    if r.status_code == 404:
        online = False
    else:
        online = True
    
    return online

def build_tiff(adate):
    """download and build geotiff"""

    joblist = [{'product':'1day','url':'https://floodlight.ssec.wisc.edu/composite/RIVER-FLDglobal-composite1_{}_000000.part{}.tif'},
            {'product':'5day','url':'https://floodlight.ssec.wisc.edu/composite/RIVER-FLDglobal-composite_{}_000000.part{}.tif'}]
    final_tiff = []
    for entry in joblist:
        tiff_file = "VIIRS_{}_composite{}_flood.tiff".format(entry['product'],adate)
        if os.path.exists(tiff_file):
            final_tiff.append(tiff_file)
            continue
        tiff_l = []
        for i in range(1,137):
            dataurl = entry['url'].format(adate,str(i).zfill(3))
            filename = dataurl.split('/')[-1]
            # try download file
            try:
                r = requests.get(dataurl, allow_redirects=True)
            except requests.RequestException as e:
                logging.warning("no download: " + dataurl)
                logging.waring('error:' + str(e))
                continue
            # may not have files for some aio
            if r.status_code == 404:
                continue
            open(filename,'wb').write(r.content)
            tiff_l.append(filename)
        vrt_file = tiff_file.replace('tiff','vrt')

        # build vrt
        vrt=gdal.BuildVRT(vrt_file, tiff_l)
        # translate to tiff
        # each tiff is 4GB in size
        gdal.Translate(tiff_file, vrt)                    
        
        # generate compressed tiff
        small_tiff = VIIRSimage + tiff_file
        gdal.Translate(small_tiff,tiff_file, options="-of GTiff -co COMPRESS=LZW -co TILED=YES" )
        
        #remove all files
        vrt=None
        os.remove(vrt_file)
        for tif in tiff_l:
            os.remove(tif)
        logging.info("generated: " + tiff_file)
        final_tiff.append(tiff_file)

    return final_tiff  

def read_data(file):
    df = pd.read_csv(file)
    df = pd.DataFrame(df)
    df.dropna(inplace=True)
    return df

def VIIRS_extract_by_mask(mask_json,tiff):
    with rasterio.open(tiff) as src:
        try:
            out_image, out_transform = mask(src, [mask_json['features'][0]['geometry']], crop=True)
        except ValueError as e:
            #'Input shapes do not overlap raster.'
            src = None
            area=0
            # return empty dataframe
            return area
    data = out_image[0]
    point_count = np.count_nonzero((data>140) & (data<201))
    src = None
    # total area
    #resolution is 375m
    area = point_count * 0.375 * 0.375
    return area

def VIIRS_extract_by_watershed(adate,tiffs):
    """extract data by wastershed"""
    
    # load watersheds
    watersheds_gdb = basepath + '/Watershed_pfaf_id.shp'
    watersheds = gpd.read_file(watersheds_gdb)
    watersheds.set_index("pfaf_id",inplace=True) 
    pfafid_list = watersheds.index.tolist()

    #VIIRS_1day_composite20210825_flood.tiff
    #VIIRS_5day_composite20210825_flood.tiff
    csv_dict = {}
    for tiff in tiffs:
        if "1day" in tiff:
            field_prefix = "oneday"
        if "5day" in tiff:
            field_prefix = "fiveday"
        csv_file = tiff.replace('.tiff','.csv')
        headers_list = ["pfaf_id",field_prefix+"Flood_Area_km",field_prefix+"perc_Area"]
        #write header
        with open(csv_file,'w') as f:   
            writer = csv.writer(f)
            writer.writerow(headers_list)
        with open(csv_file, 'a') as f:
            writer = csv.writer(f)
            for the_pfafid in pfafid_list:
                test_json = json.loads(gpd.GeoSeries([watersheds.loc[the_pfafid,'geometry']]).to_json())
                area = VIIRS_extract_by_mask(test_json,tiff)              
                perc_Area = area/watersheds.loc[the_pfafid]['area_km2']*100
                results_list = [the_pfafid,area,perc_Area]
                writer.writerow(results_list)
        csv_dict[field_prefix] = csv_file

    join = read_data(csv_dict['oneday'])
    join = join[join.onedayFlood_Area_km != 0]    

    join1 = read_data(csv_dict['fiveday'])
    join1 = join1[join1.fivedayFlood_Area_km != 0]

    merge = pd.merge(join.set_index('pfaf_id'), join1.set_index('pfaf_id'), on='pfaf_id', how='outer')
    merge.fillna(0, inplace=True) 

    #VIIRS_Flood_yyyymmdd.csv
    merged_csv = "VIIRS_Flood_{}.csv".format(adate)
    merge.to_csv(VIIRSsummary + merged_csv)  

    # need clean up
    os.remove(csv_dict['oneday'])
    os.remove(csv_dict['fiveday'])

    # remove tiff
    os.remove(tiffs[0])
    os.remove(tiffs[1])

    return
    
def VIIRS_cron():
    """ main cron script"""
    global basepath
    basepath = os.path.dirname(os.path.abspath(__file__))

    load_config()
    adate = generate_adate()

    if check_status(adate):
        logging.info("already processed: " + adate)
        return
        
    if not check_data_online(adate):
        logging.info("no data online: " + adate)
        return
    
    logging.info("Processing: " + adate)
    # change dir to VIIRSraw
    os.chdir(VIIRSraw)

    # get two tiffs
    tiffs = build_tiff(adate)
    
    # extract data from tiffs
    VIIRS_extract_by_watershed(adate,tiffs)

def main():
    VIIRS_cron()

if __name__ == "__main__":
    main()
"""Data Extraction Tool

This script extracts data from GFMS and GloFAS for a list of watersheds

This tool accepts comma separated value files (.csv)

This file can also be imported as a module and contains the following
functions:

    * 
    * 
"""

import argparse
import yaml
import requests, wget
import logging

import os,sys,json,csv
from datetime import date,timedelta,datetime

import math

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from osgeo import gdal
import geopandas
import rasterio
from rasterio.mask import mask
from rasterio import Affine # or from affine import Affine
from shapely.geometry import Point

from progressbar import progress

from GFMS_duration_fix import fix_duration
from Flood_Severity_Calculation_fix import flood_severity
from gis_output import generate_gisfile

def load_config():
    """load configuration file """
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    global ftpsite 
    ftpsite = cfg['ftp']
    global rawdata 
    global gfmsdata
    global gfmsdata_fix
    global glofasdata
    global flooddata
    global gisdata
    rawdata = cfg['datalocation']['rawdata'] + os.path.sep
    gfmsdata = cfg['datalocation']['gfmsdata'] + os.path.sep
    gfmsdata_fix = cfg['datalocation']['gfmsdata_fix'] + os.path.sep
    glofasdata = cfg['datalocation']['glofasdata'] + os.path.sep
    flooddata = cfg['datalocation']['flooddata'] + os.path.sep
    gisdata = cfg['datalocation']['gisdata'] + os.path.sep
    
    """set up logging file"""
    logging.basicConfig(filename = cfg['datalocation']['loggingfile'], format='%(asctime)s %(message)s', level=logging.INFO)

    

def GFMS_getlatest():
    """find the latest data set"""
    baseurl = "http://eagle2.umd.edu/flood/download/"
    forcast_date = date.today() + timedelta(days=10)
    cur_year, cur_month = map(str,[forcast_date.today().year,forcast_date.today().month])
    cur_month = cur_month.zfill(2)
    dataurl = baseurl + cur_year + "/" + cur_year + cur_month 
    response = requests.get(dataurl)
    raw_text = response.text.split()
    data_list = [x.split("'")[1] for x in raw_text if "href" in x]
    latest_data = data_list[-2]
    download_data_url = dataurl + "/" + latest_data
    return [latest_data, download_data_url]

def GFMS_getdownload_url(bin_file):
    """getdownload url based on a date string"""
    # Flood_byStor_2020013118.vrt
    datestr = bin_file.split("_")[2]
    baseurl = "http://eagle2.umd.edu/flood/download/"
    dataurl = baseurl + datestr[:4] + "/" +  datestr[:6]
    download_data_url = dataurl + "/" + bin_file
    return download_data_url

def GFMS_download(bin_file = False):
    """download GFMS data"""
    baseurl = "http://eagle2.umd.edu/flood/download/"
    
    if not bin_file:
        bin_file,download_data_url = GFMS_getlatest()
    else:
        download_data_url = GFMS_getdownload_url(bin_file)
        #print(download_data_url)
    # download the latest data
    if not os.path.exists(rawdata+bin_file):
        wget.download(download_data_url,out=rawdata)

    # generate header file
    hdr_header = """NCOLS 2458
    NROWS 800
    XLLCORNER -127.25
    YLLCORNER -50
    CELLSIZE 0.125
    PIXELTYPE FLOAT
    BYTEORDER LSBFIRST
    NODATA_VALUE -9999
    """
    header_file = rawdata+bin_file.replace(".bin",".hdr")
    with open(header_file,"w") as f:
        f.write(hdr_header)

    vrt_template="""<VRTDataset rasterXSize="2458" rasterYSize="800">
  <SRS>GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]</SRS>
  <GeoTransform> -1.2725000000000000e+02,  1.2500000000000000e-01,  0.0000000000000000e+00,  5.0000000000000000e+01,  0.0000000000000000e+00, -1.2500000000000000e-01</GeoTransform>
  <VRTRasterBand dataType="Float32" band="1">
    <Metadata>
      <MDI key="STATISTICS_APPROXIMATE">YES</MDI>
      <MDI key="STATISTICS_MAXIMUM">1345.408203125</MDI>
      <MDI key="STATISTICS_MEAN">26.161176808621</MDI>
      <MDI key="STATISTICS_MINIMUM">1.1765951057896e-07</MDI>
      <MDI key="STATISTICS_STDDEV">120.73468295071</MDI>
      <MDI key="STATISTICS_VALID_PERCENT">1.117</MDI>
    </Metadata>
    <NoDataValue>-9999</NoDataValue>
    <ComplexSource>
      <SourceFilename relativeToVRT="1">{}</SourceFilename>
      <SourceBand>1</SourceBand>
      <SourceProperties RasterXSize="2458" RasterYSize="800" DataType="Float32" BlockXSize="2458" BlockYSize="1" />
      <SrcRect xOff="0" yOff="0" xSize="2458" ySize="800" />
      <DstRect xOff="0" yOff="0" xSize="2458" ySize="800" />
      <NODATA>-9999</NODATA>
    </ComplexSource>
  </VRTRasterBand>
</VRTDataset>"""

    # gdalwarp -tr 0.0625 -0.0625 Flood_byStor_2020042721.bin Flood_byStor_2020042721_new.vrt
    vrt_template = """<VRTDataset rasterXSize="4916" rasterYSize="1600" subClass="VRTWarpedDataset">
  <GeoTransform> -1.2725000000000000e+02,  6.2500000000000000e-02,  0.0000000000000000e+00,  5.0000000000000000e+01,  0.0000000000000000e+00, -6.2500000000000000e-02</GeoTransform>
  <VRTRasterBand dataType="Float32" band="1" subClass="VRTWarpedRasterBand">
    <NoDataValue>-9999</NoDataValue>
  </VRTRasterBand>
  <BlockXSize>512</BlockXSize>
  <BlockYSize>128</BlockYSize>
  <GDALWarpOptions>
    <WarpMemoryLimit>6.71089e+07</WarpMemoryLimit>
    <ResampleAlg>NearestNeighbour</ResampleAlg>
    <WorkingDataType>Float32</WorkingDataType>
    <Option name="INIT_DEST">NO_DATA</Option>
    <SourceDataset relativeToVRT="1">{}</SourceDataset>
    <Transformer>
      <ApproxTransformer>
        <MaxError>0.125</MaxError>
        <BaseTransformer>
          <GenImgProjTransformer>
            <SrcGeoTransform>-127.25,0.125,0,50,0,-0.125</SrcGeoTransform>
            <SrcInvGeoTransform>1018,8,0,400,0,-8</SrcInvGeoTransform>
            <DstGeoTransform>-127.25,0.0625,0,50,0,-0.0625</DstGeoTransform>
            <DstInvGeoTransform>2036,16,0,800,0,-16</DstInvGeoTransform>
          </GenImgProjTransformer>
        </BaseTransformer>
      </ApproxTransformer>
    </Transformer>
    <BandList>
      <BandMapping src="1" dst="1">
        <SrcNoDataReal>-9999</SrcNoDataReal>
        <SrcNoDataImag>0</SrcNoDataImag>
        <DstNoDataReal>-9999</DstNoDataReal>
        <DstNoDataImag>0</DstNoDataImag>
      </BandMapping>
    </BandList>
  </GDALWarpOptions>
</VRTDataset>"""

    # generate VRT file
    vrt_file = rawdata + bin_file.replace(".bin",".vrt")
    with open(vrt_file,"w") as f:
        f.write(vrt_template.format(bin_file))

    return vrt_file

def GFMS_loader(infile, band=1):
    """load a given GFMS data file"""
    ds = gdal.Open(infile, gdal.GA_ReadOnly)
    
    # load vrt data, mask nodata
    vrt_nodata = -9999.0
    vrt_data = ds.GetRasterBand(band).ReadAsArray()
    vrt_data[vrt_data == vrt_nodata] = np.nan
    #Map extent
    trans = ds.GetGeoTransform()
    xsize = ds.RasterXSize
    ysize = ds.RasterYSize
    vrt_extent = [trans[0], trans[0] + xsize * trans[1],
            trans[3] + ysize*trans[5], trans[3]]
    
    ds = None
    return [vrt_data, vrt_extent]

def GFMS_plot(infile,savefig=True):
    """plot GFMS_data"""

    print(infile)
    bin_name = os.path.basename(infile).replace(".vrt",".bin")
    # load data
    vrt_data, vrt_ext = GFMS_loader(infile)
    fig,ax = plt.subplots()
    ax.set(xlabel='Longitude',ylabel='Latitude',title = bin_name)
    img_plot = plt.imshow(vrt_data, extent=vrt_ext,cmap="jet",vmin=0.01,vmax=200.0)
    ax.grid(True)
    if savefig:
        png_name = os.path.basename(infile).replace(".vrt",".png")
        fig.savefig(png_name)
    else:
        plt.show()

def watersheds_gdb_reader():
    """reader watersheds gdb into geopandas"""

    #watersheds_gdb = 'WRIWatersheds.gdb'
    # watersheds_gdb = 'AQID_Watwershed_Jan2020/AQID_Watwershed_Jan2020.shp'
    # watersheds = geopandas.read_file(watersheds_gdb)
    # watersheds.set_index("aqid",inplace=True)
    
    #pfaf_id, areakm2
    watersheds_gdb = 'Watersheds_032020/wastershed_prj_latlon.shp'
    watersheds = geopandas.read_file(watersheds_gdb)
    watersheds.rename(columns={"pfaf_id": "aqid"},inplace=True)
    watersheds.set_index("aqid",inplace=True)

    return watersheds

def GFMS_extract_by_mask(vrt_file,mask_json):
    """extract GFMS data for a given watershed"""

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
    d = geopandas.GeoDataFrame({'col':col,'row':row,'intensity':point_value})
    # coordinate transformation
    d['lon'] = d.apply(lambda row: rc2xy(row.row,row.col)[0], axis=1)
    d['lat'] = d.apply(lambda row: rc2xy(row.row,row.col)[1], axis=1)
    d['area'] = d.apply(lambda row: pixel_area_km2(row.lon,row.lat), axis=1)
    
    # geometry 
    d['geometry'] =d.apply(lambda row: Point(row['lon'], row['lat']), axis=1)
    # first 2 points
    src = None
    return d

def GFMS_watershed_plot(vectordata,test_aqid,vtk_file,xy_points):
    # plot polyon patch on image
    from matplotlib.patches import Polygon as mpl_Polygon
    from matplotlib.collections import PatchCollection
    from descartes import PolygonPatch

    vrt_data,vrt_ext = GFMS_loader(vtk_file)
    poly=vectordata.loc[test_aqid,'geometry']
    x1,y1,x2,y2 = vectordata.loc[[test_aqid],'geometry'].total_bounds
    fig,ax= plt.subplots()
    ax.imshow(vrt_data,extent=vrt_ext)
    ax.add_patch(PolygonPatch(poly,fc='none',ec='Blue',alpha=0.5,linewidth=3))
    if (not xy_points.empty):
        ax.scatter(xy_points.lon,xy_points.lat,color='r',s=5)
    ax.set_xlim(x1-0.2,x2+0.2)
    ax.set_ylim(y1-0.2,y2+0.2)
    ax.set(xlabel='Longitude',ylabel='Latitude',title="Watershed "+str(test_aqid)+ " "+vtk_file)
    #plt.show()
    png_name = "aqid_"+str(test_aqid) + "_" + os.path.basename(vtk_file) + ".png"
    fig.savefig(png_name)

def GFMS_extract_by_watershed(vtk_file,aqid_list,gen_plot = False):
    """extract and summary"""

    watersheds = watersheds_gdb_reader()
    if len(aqid_list) == 0:
        # take the list from watersheds gdb
        #aqid is the index column
        aqid_list = watersheds.index.tolist()
    
    # setup output file
    headers_list = ["pfaf_id","GFMS_TotalArea_km","GFMS_perc_Area","GFMS_MeanDepth","GFMS_MaxDepth","GFMS_Duration"]
    summary_file = gfmsdata + os.path.basename(vtk_file)[:-4]+ ".csv"
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
            data_points = GFMS_extract_by_mask(vtk_file, test_json)
            if gen_plot:
                GFMS_watershed_plot(watersheds,the_aqid,vtk_file,data_points)

            # generate summary
            #Summary part
            #GFMS_TotalArea_km	GFMS_perc_Area	GFMS_MeanDepth	GFMS_MaxDepth	GFMS_Duration
            # print('Summary')
            # print('Watershed: ', the_aqid)
            # print("GFMS data: ", vtk_file)
            # print("Number of data point: ", len(data_points))
            # print("GFMS_TotalArea_km2: ",data_points['area'].sum())
            # print("GFMS_perc_Area (%): ",data_points['area'].sum()/watersheds.loc[the_aqid]['SUM_area_km2']*100)
            # print("GFMS_MeanDepth (mm): ",data_points['intensity'].mean())
            # print("GFMS_MaxDepth (mm): ",data_points['intensity'].max())
            # print("GFMS_Duration (hour): ", 3)
            
            # write summary to a csv file
            GFMS_Duration = 0
            if (not data_points.empty):
                GFMS_TotalArea = data_points['area'].sum()
                if GFMS_TotalArea > 100.0:
                    GFMS_Duration = 3                
                GFMS_Area_percent = GFMS_TotalArea/watersheds.loc[the_aqid]['areakm2']*100
                GFMS_MeanDepth = data_points['intensity'].mean()
                GFMS_MaxDepth = data_points['intensity'].max()
            else:
                GFMS_TotalArea = 0.0
                GFMS_Area_percent = 0.0
                GFMS_MeanDepth = 0.0
                GFMS_MaxDepth = 0.0
                GFMS_Duration = 0.0

            results_list = [the_aqid,GFMS_TotalArea,GFMS_Area_percent,GFMS_MeanDepth,GFMS_MaxDepth,GFMS_Duration]
            writer.writerow(results_list)
        
    print(summary_file)
    logging.info("GFMS: "+ summary_file)
    # wrtie summary file as excel
    temp_data = pd.read_csv(summary_file)
    xlsx_name = summary_file.replace(".csv",".xlsx")
    sheet_name = os.path.basename(summary_file)[:-4]
    temp_data.to_excel(xlsx_name, sheet_name=sheet_name, index=False)
    
    return 

def data_extractor(aqid_csv='',bin_file=''):
    """extractor data for a list of watersheds"""

    vrt_file = GFMS_download(bin_file)
    print(vrt_file)

    aqid_list = []

    if (aqid_csv != None):
        if os.path.exists(aqid_csv):
            df = pd.read_csv(aqid_csv)
            aqid_list=df['aqid']
    
    GFMS_extract_by_watershed(vrt_file,aqid_list,gen_plot=False)

    return 

def GloFAS_process():
    """process glofas data"""

    new_files = GloFAS_download()
    #new_files = ['2020051600','2020051700','2020051800','2020051900','2020052000']
    if len(new_files) == 0:
        print ('no new file to process!')
        logging.info("no new glofas file to process!")
        sys.exit()
    
    # load watersheds data
    watersheds = watersheds_gdb_reader()
    # generate sindex
    watersheds.sindex

    for data_date in new_files:
        print("processing: " + data_date)
        fixed_sites = rawdata + "threspoints_"+data_date + ".txt" 
        dyn_sites = rawdata + "threspointsDyn_" + data_date + ".txt"
        # read fixed station data
        header_fixed_19 = ["Point No", "ID", "Basin", "Location", "Station", "Country", "Continent", "Country_code", "Upstream area", "unknown_1", "Lon", "Lat", "empty", "unknown_2", "Days_until_peak", "GloFAS_2yr", "GloFAS_5yr", "GloFAS_20yr", "Alert_level"]
        header_fixed_18 = ["Point No", "ID", "Basin", "Location", "Station", "Country", "Continent", "Country_code", "Upstream area", "Lon", "Lat", "empty", "unknown_2", "Days_until_peak", "GloFAS_2yr", "GloFAS_5yr", "GloFAS_20yr", "Alert_level"]
        fixed_data = pd.read_csv(fixed_sites,header = None,error_bad_lines=False)
        fixed_data_col = len(fixed_data.axes[1])
        if fixed_data_col == 19:
            fixed_data.columns = header_fixed_19
        elif fixed_data_col == 18:
            fixed_data.columns = header_fixed_18
        # read dynamic station data
        header_dyn_19 = ["Point No", "ID", "Station", "Basin", "Location", "Country", "Continent", "Country_code", "unknown_1","Upstream area", "Lon", "Lat", "empty", "unknown_2", "Days_until_peak", "GloFAS_2yr", "GloFAS_5yr", "GloFAS_20yr", "Alert_level"]
        header_dyn_18 = ["Point No", "ID", "Station", "Basin", "Location", "Country", "Continent", "Country_code", "Upstream area", "Lon", "Lat", "empty", "unknown_2", "Days_until_peak", "GloFAS_2yr", "GloFAS_5yr", "GloFAS_20yr", "Alert_level"]
        dyn_data = pd.read_csv(dyn_sites,header=None,error_bad_lines=False)
        dyn_data_col = len(dyn_data.axes[1])
        if dyn_data_col == 19:
            dyn_data.columns = header_dyn_19
        elif dyn_data_col == 18:
            dyn_data.columns = header_dyn_18
        # merge two datasets
        if fixed_data_col== dyn_data_col:
            total_data = fixed_data.append(dyn_data,sort=True)
        else:
            total_data = fixed_data
            print("dyn_data is ignored")

        # create a geopanda dataset
        gdf = geopandas.GeoDataFrame(
        total_data, geometry=geopandas.points_from_xy(total_data.Lon, total_data.Lat))
        gdf.crs = "EPSG:4326"
        # generate sindex
        gdf.sindex

        # sjoin 
        watersheds.crs = "EPSG:4326"
        gdf_watersheds = geopandas.sjoin(gdf, watersheds, op='within')
        gdf_watersheds.rename(columns={"index_right":"pfaf_id"},inplace=True)

        forcast_time = (fixed_sites.split("_")[1]).replace('00.txt','')
        forcast_time = datetime.strptime(forcast_time, '%Y%m%d' )
        # add column "Forecast Date"
        gdf_watersheds["Forecast Date"]=forcast_time.isoformat()

        # convert "GloFAS_2yr","GloFAS_5yr","GloFAS_20y" to 0~100
        gdf_watersheds["GloFAS_2yr"] = gdf_watersheds["GloFAS_2yr"]*100
        gdf_watersheds["GloFAS_5yr"] = gdf_watersheds["GloFAS_5yr"]*100
        gdf_watersheds["GloFAS_20yr"] = gdf_watersheds["GloFAS_20yr"]*100
        gdf_watersheds=gdf_watersheds.astype({"GloFAS_2yr":int,"GloFAS_5yr":int,"GloFAS_20yr":int})

        # fill max_EPS
        gdf_watersheds["max_EPS"]=gdf_watersheds.apply(lambda row: str(row['GloFAS_2yr'])+"/"+str(row['GloFAS_5yr'])+"/"+str(row['GloFAS_20yr']), axis=1)

        # write out csv file
        out_csv = glofasdata + "threspoints_" + data_date + ".csv"
        out_columns =['Point No',"Station","Basin","Country","Lat","Lon","Upstream area","Forecast Date","max_EPS",
                    "GloFAS_2yr","GloFAS_5yr","GloFAS_20yr","Alert_level","Days_until_peak","pfaf_id"]
        gdf_watersheds.to_csv(out_csv,index=False,columns=out_columns,float_format='%.3f')
        
        logging.info("glofas: " + out_csv)

        # write to excel
        out_excel = glofasdata + "threspoints_" + data_date + ".xlsx"
        gdf_watersheds.to_excel(out_excel,index=False,columns=out_columns,sheet_name='Sheet_name_1')
        
        # to geojson
        out_geojson = glofasdata + "threspoints_" + data_date + ".geojson"
        gdf_watersheds.to_file(out_geojson,driver='GeoJSON')
    
    return new_files

def GloFAS_download():
    '''download glofas data from ftp'''
    
    from ftplib import FTP
    ftp = FTP(host=ftpsite['host'],user=ftpsite['user'],passwd=ftpsite['passwd'])
    ftp.cwd(ftpsite['directory'])
    file_list = ftp.nlst()
    job_list = []
    for txt in file_list:
        if os.path.exists(rawdata+txt):
            continue
        with open(rawdata+txt, 'wb') as fp:
            #print("ftp: " + txt)
            ftp.retrbinary('RETR '+txt, fp.write)
            #threspoints_2020042800.txt threspointsDyn_2020052100.txt
            if ("threspoints_"  in txt):
                job_list.append((txt.split(".")[0]).replace("threspoints_",""))
    ftp.quit()
    
    return job_list

def run_cron():
    """run cron job"""
    # cron steup cd ~/ModelofModels/data && python datatool.py --cron
    # run every three hours
    # edit: crontab -e 
    # 5 0,3,6,9,12,15,18,21 * * * commnad

    # it is likly only one date: 2020051600
    processing_dates = GloFAS_process()
    # check if GMS data is available 
    #processing_dates = ['2020061800','2020061900','2020062000']
    binhours = ["00","03","06","09","12","15","18","21"]
    for data_date in processing_dates:
        # find the previous one
        real_date = data_date[:-2]
        for binhour in binhours:
            bin_file = "Flood_byStor_" + real_date + binhour + ".bin"
            print(bin_file)
            # process bin file
            data_extractor(aqid_csv = None,bin_file=bin_file)
        
        # need to run duration caculation
        previous_date = datetime.strptime(real_date,"%Y%m%d") - timedelta(days=1)
        base0= "Flood_byStor_" + previous_date.strftime("%Y%m%d") + "21.csv"
        fix_list = ["Flood_byStor_" + real_date + x + ".csv" for x in binhours]
        fix_list.insert(0,base0)

        # call fix duration
        fix_duration(fix_list,folder=gfmsdata,fixfolder=gfmsdata_fix)

        # flood severity calculation
        # flood_severity(gfmscsv,glofascsv,date)
        gfmscsv = gfmsdata_fix + "Flood_byStor_" + data_date + ".csv"
        glofascsv = glofasdata + "threspoints_" + data_date + ".csv"
        flood_severity(gfmscsv,glofascsv,real_date,flooddata)
        logging.info("Flood: "+ real_date)
        # generate GIS output file
        flood_file = flooddata + 'Attributes_Clean_'+ real_date + '.csv'
        generate_gisfile(flood_file, real_date, gisdata)

def run_cron_fix(adate):
    """run cron job"""
    # cron steup cd ~/ModelofModels/data && python datatool.py --cron
    # run every three hours
    # edit: crontab -e 
    # 5 0,3,6,9,12,15,18,21 * * * commnad

    # it is likly only one date: 2020051600
    #processing_dates = GloFAS_process()
    # check if GMS data is available 
    #processing_dates = ['2020061800','2020061900','2020062000']
    processing_dates = [ adate ]
    
    binhours = ["00","03","06","09","12","15","18","21"]
    for data_date in processing_dates:
        # find the previous one
        real_date = data_date[:-2]
        for binhour in binhours:
            bin_file = "Flood_byStor_" + real_date + binhour + ".bin"
            print(bin_file)
            # process bin file
            data_extractor(aqid_csv = None,bin_file=bin_file)
        
        # need to run duration caculation
        previous_date = datetime.strptime(real_date,"%Y%m%d") - timedelta(days=1)
        base0= "Flood_byStor_" + previous_date.strftime("%Y%m%d") + "21.csv"
        fix_list = ["Flood_byStor_" + real_date + x + ".csv" for x in binhours]
        fix_list.insert(0,base0)

        # call fix duration
        fix_duration(fix_list,folder=gfmsdata,fixfolder=gfmsdata_fix)

        # flood severity calculation
        # flood_severity(gfmscsv,glofascsv,date)
        gfmscsv = gfmsdata_fix + "Flood_byStor_" + data_date + ".csv"
        glofascsv = glofasdata + "threspoints_" + data_date + ".csv"
        flood_severity(gfmscsv,glofascsv,real_date,flooddata)
        logging.info("Flood: "+ real_date)
        # generate GIS output file
        flood_file = flooddata + 'Attributes_Clean_'+ real_date + '.csv'
        generate_gisfile(flood_file, real_date, gisdata)


def debug():
    """testing code goes here"""
    #vrt_file = GFMS_download()
    vrt_file = GFMS_download(bin_file="Flood_byStor_2020042721.bin")
    #vrt_file='Flood_byStor_2020042721.vrt'
    aqids_test=[172964]
    #aqids_test=[2538,2570,2599,2586,1902]
    #GFMS_plot(vrt_file,savefig=False)
    # Summary
    # Watershed:  2538
    # GFMS data:  Flood_byStor_2020013118.bin
    # Number of data point:  95
    # GFMS_TotalArea_km2:  18157.84724419623
    # GFMS_perc_Area (%):  29.926544050542685
    # GFMS_MeanDepth (mm):  3.4248955249786377
    # GFMS_MaxDepth (mm):  26.457630157470703
    #print(vrt_file)
    GFMS_extract_by_watershed(vrt_file,aqids_test,gen_plot=True)
    sys.exit()

def main():

    load_config()
    #debug()
    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-w','--watersheds',type=str,help="file contains list of watetsheds (aqid)")
    parser.add_argument(
        "-b","--bin", type=str, help="specific GFMS bin file")
    parser.add_argument('-gl','--glofas', dest='glofas', action="store_true", help="process glofas data")
    parser.add_argument('-cr','--cron', dest='cron', action="store_true", help="run as a cron job")
    parser.add_argument('-fd','--fixdate', dest='fixdate', type=str, help="rerun a cron job on a certian day")

    args = parser.parse_args()
    if (args.glofas):
        GloFAS_process()
    elif (args.cron):
        run_cron()
    elif (args.fixdate):
        run_cron_fix(args.fixdate)
    else:
        data_extractor(aqid_csv = args.watersheds,bin_file=args.bin)

if __name__ == "__main__":
    main()
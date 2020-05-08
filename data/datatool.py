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

import os,sys,json,csv
from datetime import date,timedelta
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

def load_config():
    """load configuration file """
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    global ftpsite 
    ftpsite = cfg['ftp']
    global rawdata 
    rawdata = cfg['datalocation']['rawdata'] + os.path.sep

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
    if not os.path.exists(bin_file):
        wget.download(download_data_url)

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
    header_file = bin_file.replace(".bin",".hdr")
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
    vrt_file = bin_file.replace(".bin",".vrt")
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

    bin_name = infile.replace(".vrt",".bin")
    # load data
    vrt_data, vrt_ext = GFMS_loader(infile)
    fig,ax = plt.subplots()
    ax.set(xlabel='Longitude',ylabel='Latitude',title = bin_name)
    img_plot = plt.imshow(vrt_data, extent=vrt_ext,cmap="jet",vmin=0.01,vmax=200.0)
    ax.grid(True)
    if savefig:
        png_name = infile.replace(".vrt",".png")
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
    png_name = "aqid_"+str(test_aqid) + "_" + vtk_file + ".png"
    fig.savefig(png_name)

def GFMS_extract_by_watershed(vtk_file,aqid_list,gen_plot = False):
    """extract and summary"""

    watersheds = watersheds_gdb_reader()
    if len(aqid_list) == 0:
        # take the list from watersheds gdb
        #aqid is the index column
        aqid_list = watersheds.index.tolist()
    
    count = 0
    for the_aqid in aqid_list:
        count += 1
        print(the_aqid, count, " out of ", len(aqid_list))

        # extract mask
        test_json = json.loads(geopandas.GeoSeries([watersheds.loc[the_aqid,'geometry']]).to_json())
        # plot check
        data_points = GFMS_extract_by_mask(vtk_file, test_json)
        if gen_plot:
            GFMS_watershed_plot(watersheds,the_aqid,vtk_file,data_points)

        # generate summary
        #Summary part
        #GFMS_TotalArea_km	GFMS_%Area	GFMS_MeanDepth	GFMS_MaxDepth	GFMS_Duration
        # print('Summary')
        # print('Watershed: ', the_aqid)
        # print("GFMS data: ", vtk_file)
        # print("Number of data point: ", len(data_points))
        # print("GFMS_TotalArea_km2: ",data_points['area'].sum())
        # print("GFMS_%Area (%): ",data_points['area'].sum()/watersheds.loc[the_aqid]['SUM_area_km2']*100)
        # print("GFMS_MeanDepth (mm): ",data_points['intensity'].mean())
        # print("GFMS_MaxDepth (mm): ",data_points['intensity'].max())
        # print("GFMS_Duration (hour): ", 3)
        
        # write summary to a csv file
        GFMS_Duration = 3
        if (not data_points.empty):
            GFMS_TotalArea = data_points['area'].sum()
            GFMS_Area_percent = GFMS_TotalArea/watersheds.loc[the_aqid]['areakm2']*100
            GFMS_MeanDepth = data_points['intensity'].mean()
            GFMS_MaxDepth = data_points['intensity'].max()
        else:
            GFMS_TotalArea = 0.0
            GFMS_Area_percent = 0.0
            GFMS_MeanDepth = 0.0
            GFMS_MaxDepth = 0.0

        headers_list = ["pfaf_id","GFMS_TotalArea_km","GFMS_%Area","GFMS_MeanDepth","GFMS_MaxDepth","GFMS_Duration"]
        results_list = [the_aqid,GFMS_TotalArea,GFMS_Area_percent,GFMS_MeanDepth,GFMS_MaxDepth,GFMS_Duration]

        summary_file = "Summary_" + vtk_file[:-4]+ ".csv"
        if not os.path.exists(summary_file):
            with open(summary_file,'w') as f:
                writer = csv.writer(f)
                writer.writerow(headers_list)  
        
        with open(summary_file, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(results_list)
    
    print(summary_file)

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
            job_list.append(txt)
    ftp.quit()
       

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
    # GFMS_%Area (%):  29.926544050542685
    # GFMS_MeanDepth (mm):  3.4248955249786377
    # GFMS_MaxDepth (mm):  26.457630157470703
    #print(vrt_file)
    GFMS_extract_by_watershed(vrt_file,aqids_test,gen_plot=True)
    sys.exit()

def main():

    #debug()
    
    #load_config()
    #GloFAS_download()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-w','--watersheds',type=str,help="file contains list of watetsheds (aqid)")
    parser.add_argument(
        "-b","--bin", type=str, help="specific GFMS bin file")
    args = parser.parse_args()
    data_extractor(aqid_csv = args.watersheds,bin_file=args.bin)

if __name__ == "__main__":
    main()
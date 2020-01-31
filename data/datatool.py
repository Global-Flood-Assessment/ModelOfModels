"""Data Extraction Tool

This script extracts data from GFMS and GloFAS for a list of watersheds

This tool accepts comma separated value files (.csv)

This file can also be imported as a module and contains the following
functions:

    * 
    * 
"""

import argparse

import requests, wget
import os,sys,json
from datetime import date
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

def GFMS_getlatest():
    """find the latest data set"""
    baseurl = "http://eagle2.umd.edu/flood/download/"
    cur_year, cur_month = map(str,[date.today().year,date.today().month])
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

    watersheds_gdb = 'WRIWatersheds.gdb'
    watersheds = geopandas.read_file(watersheds_gdb)
    watersheds.set_index("aqid",inplace=True)
    return watersheds

def GFMS_extract_by_mask(vrt_file,mask_json):
    """extract GFMS data for a given watershed"""

    #print(vrt_file)
    #print(mask_json['features'][0]['geometry'])
    with rasterio.open(vrt_file) as src:
        out_image, out_transform = mask(src, [mask_json['features'][0]['geometry']], crop=True)
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
    pixel_area_km2 = lambda lon, lat: 111.111*111.111*math.cos(lat*0.01745)*0.125*0.125 
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
    ax.scatter(xy_points.lon,xy_points.lat,color='r',s=5)
    ax.set_xlim(x1-0.2,x2+0.2)
    ax.set_ylim(y1-0.2,y2+0.2)
    ax.set(xlabel='Longitude',ylabel='Latitude',title="Watershed "+str(test_aqid)+ " "+vtk_file)
    plt.show()

def GFMS_extract_by_watershed(vtk_file,the_aqid,gen_plot = False):
    """extract and summary"""

    watersheds = watersheds_gdb_reader()
    test_json = json.loads(geopandas.GeoSeries([watersheds.loc[the_aqid,'geometry']]).to_json())
    # plot check
    data_points = GFMS_extract_by_mask(vtk_file, test_json)
    if (not data_points.empty) and gen_plot:
        GFMS_watershed_plot(watersheds,the_aqid,vtk_file,data_points)

    # generate summary
    #Summary part
    #GFMS_TotalArea_km	GFMS_%Area	GFMS_MeanDepth	GFMS_MaxDepth	GFMS_Duration
    print('Summary')
    print('Watershed: ', the_aqid)
    print("GFMS data: ", vtk_file)
    print("Number of data point: ", len(data_points))
    print("GFMS_TotalArea_km2: ",data_points['area'].sum())
    print("GFMS_%Area (%): ",data_points['area'].sum()/watersheds.loc[the_aqid]['SUM_area_km2']*100)
    print("GFMS_MeanDepth (mm): ",data_points['intensity'].mean())
    print("GFMS_MaxDepth (mm): ",data_points['intensity'].max())
    print("GFMS_Duration (hour): ", 3)
    
    return data_points

def data_extractor(file_loc,):
    """extractor data for a list of watersheds

    Parameters
    ----------
    file_loc : str
        The file location of the spreadsheet

    Returns
    -------
    list
    """
    list_watersheds = pd.read_csv(file_loc)
    # aqid
    aqid = [2538]
    GFMS_bin = ['Flood_byStor_2020012018.bin']

    return 

def debug():
    """testing code goes here"""
    #vrt_file = GFMS_download()
    vrt_file = GFMS_download(bin_file='Flood_byStor_2020013118.bin')
    aqid=2538
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
    GFMS_extract_by_watershed(vrt_file,2538,gen_plot=False)
    sys.exit()

def main():

    debug()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'input_file',
        type=str,
        help="List of watetsheds (aqid)"
    )
    args = parser.parse_args()
    data_extractor(args.input_file)


if __name__ == "__main__":
    main()
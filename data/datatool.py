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

def GFMS_download():
    """download GFMS data"""
    baseurl = "http://eagle2.umd.edu/flood/download/"
    # find the latest data set
    cur_year, cur_month = map(str,[date.today().year,date.today().month])
    cur_month = cur_month.zfill(2)
    dataurl = baseurl + cur_year + "/" + cur_year + cur_month 
    response = requests.get(dataurl)
    raw_text = response.text.split()
    data_list = [x.split("'")[1] for x in raw_text if "href" in x]
    latest_data = data_list[-2]
    latest_data_url = dataurl + "/" + latest_data
    print(latest_data_url)

    # download the latest data
    if not os.path.exists(latest_data):
        wget.download(latest_data_url)

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
    header_file = latest_data.replace(".bin",".hdr")
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
    vrt_file = latest_data.replace(".bin",".vrt")
    with open(vrt_file,"w") as f:
        f.write(vrt_template.format(latest_data))
    print(vrt_file)
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


def main():
    
    vrt_file = GFMS_download()
    GFMS_plot(vrt_file,savefig=False)

    sys.exit()

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
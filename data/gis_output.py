"""
    gis_output.py
        -- generate shaplefile, kml outputs from flood severity 
"""

import os,sys,json,csv
import zipfile

import pandas as pd
import geopandas
import fiona 

def generate_gisfile(flood_csv,real_date,out_folder):
    """ generate gis file from the flood severity """

    # load watersheds
    watersheds_gdb = 'Watersheds_032020/wastershed_prj_latlon.shp'
    watersheds = geopandas.read_file(watersheds_gdb)
    watersheds.set_index("pfaf_id",inplace=True)

    result_df = pd.read_csv(flood_csv) 
    warning_df = result_df[result_df.Alert == "Warning"]
    out_df = watersheds.loc[warning_df['pfaf_id']]
    out_df = out_df.merge(warning_df, left_on='pfaf_id', right_on='pfaf_id')
    # write warning result to geojson
    result_geojson = out_folder + "flood_warning_" + real_date + ".geojson"
    out_df.to_file(result_geojson, index=True, driver='GeoJSON')    # generate a zip file    
    # write warning result to shapefile
    result_shp = out_folder + "flood_warning_" + real_date + ".shp"
    out_df.to_file(result_shp, index=True,encoding='utf-8')

    result_kml = out_folder + "flood_warning_" + real_date + ".kml"
    # !ogr2ogr -f 'KML' -a_srs EPSG:4326 $result_kml $result_geojson
    geopandas.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
    geopandas.io.file.fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'
    out_df.to_file(result_kml, driver='KML')

    # flood_warning_20200617.cpg
    # flood_warning_20200617.prj
    # flood_warning_20200617.dbf
    # flood_warning_20200617.shp
    # flood_warning_20200617.geojson 
    # flood_warning_20200617.shx
    # flood_warning_20200617.kml
    file_prefix = out_folder + "flood_warning_" + real_date
    file_types = ['cpg','prj','dbf','shp','shx','geojson','kml']
    zip_file = file_prefix + ".zip"
    with zipfile.ZipFile(zip_file, 'w',zipfile.ZIP_DEFLATED) as zipObj:
        for ftype in file_types:
            filename = file_prefix + "." + ftype 
            # Add file to zip
            zipObj.write(filename, os.path.basename(filename))
    # remove shpfile
    file_types = ['cpg','prj','dbf','shp','shx']
    for ftype in file_types:
        filename = file_prefix + "." + ftype 
        os.remove(filename)
        
    return 

def main():

    flood = "testdata/flood/Final_Attributes_20200617.csv"
    flood_date = "20200617"
    out_folder = "testdata/gis_output/"
    generate_gisfile(flood, flood_date, out_folder)

if __name__ == "__main__":
    main()
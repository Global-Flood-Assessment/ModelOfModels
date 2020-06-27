"""
    gis_output.py
        -- generate shaplefile, kml outputs from flood severity 
"""

import os,sys,json,csv

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
    out_df.to_file(result_geojson, index=True, driver='GeoJSON')
    # write warning result to shapefile
    result_shp = out_folder + "flood_warning_" + real_date + ".shp"
    out_df.to_file(result_shp, index=True)

    result_kml = out_folder + "flood_warning_" + real_date + ".kml"
    # !ogr2ogr -f 'KML' -a_srs EPSG:4326 $result_kml $result_geojson
    geopandas.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
    out_df.to_file(result_kml, driver='KML')
    
    return 

def main():

    flood = "testdata/flood/Final_Attributes_20200617.csv"
    flood_date = "20200617"
    out_folder = "testdata/gis_output/"
    generate_gisfile(flood, flood_date, out_folder)

if __name__ == "__main__":
    main()
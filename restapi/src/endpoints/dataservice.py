"""
    dataservice.py
        -- generate GIS output
"""
from . dataConfig import conf_dict

import os
import pandas as pd
import geopandas

def generateGISoutput(momfile,outputfile,output_type = "geojson"):
    """generate GIS output"""

    # load watersheds
    watersheds_gdb = conf_dict['watersheds']
    watersheds = geopandas.read_file(watersheds_gdb)
    watersheds.set_index("pfaf_id",inplace=True)
    
    result_df = pd.read_csv(momfile) 
    warning_df = result_df[result_df.Alert == "Warning"]
    out_df = watersheds.loc[warning_df['pfaf_id']]
    out_df = out_df.merge(warning_df, left_on='pfaf_id', right_on='pfaf_id')
    # write warning result to geojson
    out_df.to_file(outputfile, index=True, driver='GeoJSON')   

    return

def getGISdata(datatype,adate,aformat):
    """
        return GISdata
    """

    # first check if geojson in cache
    gisfile = '{type}/{type}_{date}.{format}'.format(type=datatype,date=adate,format=aformat)
    gisfile_path = conf_dict['cache'] + gisfile

    if os.path.exists(gisfile_path):
        return gisfile_path
    
    # then check if there is the product
    momfile = conf_dict[datatype+"_MoM"].format(date=adate)
    momfile_path = conf_dict[datatype] + momfile
    if os.path.exists(momfile_path):
        generateGISoutput(momfile_path,gisfile_path)
    else:
        return "error: no data found"

    return gisfile_path

def main():
    """ simple test script"""

    atype ="HWRF"
    adate ="2021082918"
    aformat = "geojson" 
    file_path = getGISdata(atype,adate,aformat)
    print(file_path)

    atype ="VIIRS"
    adate ="2021082918"
    aformat = "geojson" 
    file_path = getGISdata(atype,adate,aformat)
    print(file_path)

if __name__ == "__main__":
    main()
"""
    dataservice.py
        -- generate GIS output
"""
from . dataConfig import conf_dict

import os
import pandas as pd
import geopandas
from glob import glob

def generateGISoutput(momfile,outputfile,output_type = "geojson"):
    """generate GIS output"""

    # load watersheds
    watersheds_gdb = conf_dict['watersheds']
    watersheds = geopandas.read_file(watersheds_gdb)
    watersheds.set_index("pfaf_id",inplace=True)
    
    result_df = pd.read_csv(momfile) 
    warning_df = result_df[result_df.Alert == "Warning"]
    if output_type == "csv":
        warning_df.to_csv(outputfile, index=False)
        return

    out_df = watersheds.loc[warning_df['pfaf_id']]
    out_df = out_df.merge(warning_df, left_on='pfaf_id', right_on='pfaf_id')
    # write warning result to geojson
    if output_type == 'geojson':
        out_df.to_file(outputfile, index=True, driver='GeoJSON')   
    
    # write kml output
    if output_type == 'kml':
        geojsonf = outputfile.replace(".kml",".geojson")
        if not os.path.exists(geojsonf):
            out_df.to_file(geojsonf, index=True, driver='GeoJSON')
        import subprocess
        ogrcmd = "ogr2ogr -f KML {kml} {geojson}".format(kml = outputfile, geojson = geojsonf)
        subprocess.call(ogrcmd,shell=True)   
        # geopandas.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
        # geopandas.io.file.fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'
        # out_df.to_file(outputfile, driver='KML')
   
    return

def getLatest(apath, afile):
    """find the latest data"""

    filep = afile[:8]+ "*" + afile[-4:]
    names = [os.path.basename(x) for x in glob(apath + filep)]
    latest = sorted(names)[-1]

    return latest

def getGISdata(datatype,adate,aformat):
    """
        return GISdata
    """

    # first check if geojson in cache
    gisfile = '{type}/{type}_{date}.{format}'.format(type=datatype,date=adate,format=aformat)
    gisfile_path = conf_dict['cache'] + gisfile

    if os.path.exists(gisfile_path):
        return gisfile_path
    
    # return latest 
    if adate.lower() == 'latest':
        momfile = getLatest(conf_dict[datatype],conf_dict[datatype+"_MoM"])
    else:
        # then check if there is the product
        momfile = conf_dict[datatype+"_MoM"].format(date=adate)
    
    momfile_path = conf_dict[datatype] + momfile
    if os.path.exists(momfile_path):
        generateGISoutput(momfile_path,gisfile_path,output_type = aformat)
    else:
        return "error: no data found"

    return gisfile_path

def main():
    """ simple test script"""

    atype ="HWRF"
    adate ="2021082918"
    aformat = "kml" 
    file_path = getGISdata(atype,adate,aformat)
    print(file_path)

    atype ="VIIRS"
    adate ="2021082918"
    aformat = "geojson" 
    file_path = getGISdata(atype,adate,aformat)
    print(file_path)

if __name__ == "__main__":
    main()
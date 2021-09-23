"""
    dataservice.py
        -- generate GIS output
"""
from dataConfig import conf_dict

import os

def generateGISoutput(momfile,outputfile,output_type = "geojson"):
    """generate GIS output"""

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
        return "no data: " + momfile_path
    return gisfile_path

def main():
    """ simple test script"""

    atype ="HWRF"
    adate ="2021092206"
    aformat = "geojson" 
    file_path = getGISdata(atype,adate,aformat)
    print(file_path)

if __name__ == "__main__":
    main()
"""
    dataConfig.py
        -- folder configuration
"""

import os

home = os.path.expanduser("~")
if os.path.exists(home + "/Projects"):
    home = home + "/Projects"

conf_dict = {}
conf_dict['home'] = home
conf_dict['HWRF'] = home + "/ModelofModels/data/cron_data/HWRF/HWRF_MoM/"
# HH can be 00,06,12,18
conf_dict['HWRF_MoM'] = "Attributes_Clean_{date}HWRFUpdated.csv"

conf_dict['DFO'] = home + "/ModelofModels/data/cron_data/DFO/DFO_MoM/"
conf_dict['DFO_MoM'] = "Attributes_Clean_{date}MOM+DFOUpdated.csv" 

conf_dict['VIIRS'] = home + "/ModelofModels/data/cron_data/VIIRS/VIIRS_MoM/"
# HH can be 18
conf_dict['VIIRS_MoM'] = "Attributes_clean_{date}MOM+DFO+VIIRSUpdated.csv"

# cache folder structure
# apidata/cache/product/product_adate.geojson
conf_dict['cache'] = home + "/ModelofModels/data/apidata/"

conf_dict['watersheds'] = home + "/ModelofModels/VIIRS_Processing/Watershed_pfaf_id.shp"

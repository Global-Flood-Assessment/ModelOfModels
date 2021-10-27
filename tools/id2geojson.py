"""
    id2geojson.py
        -- watershed_id in csv file to geojson
"""

import sys, os, csv, json
import argparse
import pandas as pd
import geopandas as gpd

def id2geojson(idlist_csv,idfield = 'pfaf_id'):
    """
        convert idlist in csv to geojson
    """
    print(idlist_csv)
    # load csv file
    df =  pd.read_csv(idlist_csv)
    # force id as int
    df[idfield] = df[idfield].astype(int)
    # drop duplicates 
    df = df.drop_duplicates(subset=[idfield])
    print(df.head())

    watersheds_gdb = "../VIIRS_Processing/Watershed_pfaf_id.shp"
    watersheds = gpd.read_file(watersheds_gdb)
    watersheds.set_index("pfaf_id",inplace=True)

    out_df = watersheds.loc[df[idfield]]
    out_df = out_df.merge(df, left_on=idfield, right_on=idfield)
    # write warning result to geojson
    outputfile = idlist_csv.split(".")[0] + ".geojson"
    out_df.to_file(outputfile, index=False, driver='GeoJSON')   

    return

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('idlist', type=str, help="csv file contains pfaf_id")
    args = parser.parse_args()

    id2geojson(args.idlist)


if __name__ == "__main__":
    main()
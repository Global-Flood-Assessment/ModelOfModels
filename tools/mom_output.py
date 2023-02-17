"""
    mom_output.py
        -- extract output from mom
    paramters:
        -- pfafidlist: a csv file has pfaf_id column
        -- timeperiod: YYYYMMDD-YYYYMMDD
    output:
        -- wastersheds.geojson: wastersheds in the list
        -- two geojsons for each PDC_final output:
            -- Warning
            -- Watch
        -- CSV output:
            -- header: pfaf_id, [dates]
            -- value: pfaf_id, [Severity] 
    example:
        python mom_output.py impacted_watershed.csv 20220800-20220831 pakistan2022
"""

import argparse
import csv
import json
import os
import sys

import geopandas as gpd
import pandas as pd
import requests
from bs4 import BeautifulSoup

MOM_DOWNLOAD_FOLDER = "pdc_final"


def download_mom(starttime, endtime):
    """download mom output in a time period"""
    baseurl = "https://mom.tg-ear190027.projects.jetstream-cloud.org/ModelofModels/Final_Alert/"
    reqs = requests.get(baseurl)
    soup = BeautifulSoup(reqs.text, "html.parser")

    start_mom = "Final_Attributes_{}HWRF+MOM+DFO+VIIRSUpdated_PDC.csv".format(starttime)
    end_mom = "Final_Attributes_{}HWRF+MOM+DFO+VIIRSUpdated_PDC.csv".format(endtime)

    mom_list = []
    for link in soup.find_all("a"):
        fstr = link.string
        if not "csv" in fstr:
            continue
        if fstr >= start_mom and fstr <= end_mom:
            mom_list.append(fstr)
            if not os.path.exists(os.path.join(MOM_DOWNLOAD_FOLDER, fstr)):
                dataurl = os.path.join(baseurl, fstr)
                wgetcmd = "wget -nc " + dataurl + " -P " + MOM_DOWNLOAD_FOLDER
                os.system(wgetcmd)
    mom_list.sort()
    return mom_list


def merge_mom(df_ids, momfiles):
    """merge mom output to one csv"""
    filed_list = ["Severity", "Flag", "Alert"]
    for mom_field in filed_list:
        joined_df = df_ids.copy()
        joined_df.set_index("pfaf_id", inplace=True)

        total_file = len(momfiles)
        for count, mom in enumerate(momfiles):
            print("processing {} / {}".format(count, total_file))
            mom_df = pd.read_csv(
                os.path.join(MOM_DOWNLOAD_FOLDER, mom), encoding="ISO-8859-1"
            )
            mom_df = mom_df[["pfaf_id", mom_field]]
            mom_df = mom_df.drop_duplicates(subset=["pfaf_id"])
            # Final_Attributes_2022081606HWRF+MOM+DFO+VIIRSUpdated_PDC.csv
            datestr = mom[17 : 17 + 10]
            # rename alert
            mom_df.rename(columns={mom_field: datestr}, inplace=True)
            mom_df.set_index("pfaf_id", inplace=True)
            # merge stuff
            joined_df = joined_df.join(mom_df, how="left")
            mom_df = None

        joined_df.to_csv(f"momoutput_{mom_field}.csv", index=True, float_format="%.3f")
        joined_df = None


def extract_mom(csvfile, timeperiod, outputfolder):
    """extract mom outputs"""

    # load list of watersheds
    df = pd.read_csv(csvfile)
    df = df[["pfaf_id"]]

    # check the folder
    mom_folder = os.path.join(outputfolder, MOM_DOWNLOAD_FOLDER)
    if not os.path.exists(mom_folder):
        os.makedirs(mom_folder)
    os.chdir(outputfolder)

    start_t, end_t = timeperiod.split("-")
    start_t += "00"
    end_t += "18"
    mom_list = download_mom(start_t, end_t)

    # extract mom output to one file
    merge_mom(df, mom_list)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("idlist", type=str, help="csv file contains pfaf_id")
    parser.add_argument("timeperiod", type=str, help="time period: YYYYMMDD-YYYYMMDD")
    parser.add_argument("outputfolder", type=str, help="output folder")
    args = parser.parse_args()
    extract_mom(args.idlist, args.timeperiod, args.outputfolder)


if __name__ == "__main__":
    main()

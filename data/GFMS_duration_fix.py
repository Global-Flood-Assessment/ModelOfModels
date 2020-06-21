""" GFMS_duration_fix.py
    --fix duration issue
        -- duration is 3 only if the watershed area is flooded more than 100 sq km
        --  after every 3 hours if the flooding persists for the same watershed another 3 hours 
"""

import os,sys
import numpy as np
import pandas as pd


def fix_duration(csv_list,folder="data/gfms/",fixfolder="data/gfms_fix/"):
    """ fix duration """

    # two step procedure
    # step 1: duration is 3 only if the watershed area is flooded more than 100 sq km
    # for name in csv_list:
    #     csv_file = folder + name.replace('.bin','.csv')
    #     new_csv = csv_file.replace("gfms","gfms_fix")
    #     if os.path.exists(new_csv):
    #         continue
    #     df = pd.read_csv(csv_file)
    #     df['GFMS_Duration'] = df.apply(lambda row: 3 if (row.GFMS_TotalArea_km > 100.0) else '0', axis = 1)
    #     # write a csv file
    #     print('fix',name)
    #     df.to_csv(new_csv, index=False)

    # step 2 recount duration
    csv_file = fixfolder + csv_list[0].replace('.bin','.csv')
    # load df0
    df0 = pd.read_csv(csv_file)
    for name in csv_list[1:]:
        csv_file = folder + name.replace('.bin','.csv')
        #new_csv = csv_file.replace("gfms","gfms_fix")
        df = pd.read_csv(csv_file)
        # add two duration data
        #print(df['pfaf_id'])
        #print(df0['pfaf_id'])
        df['GFMS_Duration0'] = df['pfaf_id'].map(df0.set_index('pfaf_id')['GFMS_Duration'])
        df['GFMS_Duration'] = df.apply(lambda row: 3 + int(row.GFMS_Duration0) if (row.GFMS_TotalArea_km > 100.0) else '0', axis = 1)
        # del 
        del df['GFMS_Duration0']
        fix_csv = fixfolder + name.replace('.bin','.csv')
        print(fix_csv)
        df.to_csv(fix_csv,index=False)
        df0 = None
        df0 = df
        df = None
    return



def main():
    GFMS_list = ["Flood_byStor_2020061621.csv",
"Flood_byStor_2020061700.csv",
"Flood_byStor_2020061703.csv",
"Flood_byStor_2020061706.csv",
"Flood_byStor_2020061709.csv",
"Flood_byStor_2020061712.csv",
"Flood_byStor_2020061715.csv",
"Flood_byStor_2020061718.csv",
"Flood_byStor_2020061721.csv",]
    fix_duration(GFMS_list,folder="testdata/gfms/",fixfolder = "testdata/gfms_fix/")

if __name__ == "__main__":
    main()

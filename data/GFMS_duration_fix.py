""" GFMS_duration_fix.py
    --fix duration issue
        -- duration is 3 only if the watershed area is flooded more than 100 sq km
        --  after every 3 hours if the flooding persists for the same watershed another 3 hours 
"""

import os,sys
import numpy as np
import pandas as pd


def fix_duration(csv_list,folder="data/gfms/"):
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
    csv_file = folder + csv_list[0].replace('.bin','.csv')
    #new_csv = csv_file.replace("gfms","gfms_fix2")
    # load df0
    df0 = pd.read_csv(csv_file)
    for name in csv_list[1:]:
        csv_file = folder + name.replace('.bin','.csv')
        #new_csv = csv_file.replace("gfms","gfms_fix")
        df = pd.read_csv(csv_file)
        # add two duration data
        df['GFMS_Duration0'] = df['pfaf_id'].map(df0.set_index('pfaf_id')['GFMS_Duration'])
        df['GFMS_Duration'] = df.apply(lambda row: 3 + int(row.GFMS_Duration0) if (row.GFMS_TotalArea_km > 100.0) else '0', axis = 1)
        # del 
        del df['GFMS_Duration0']
        fix_csv = csv_file.replace("gfms","gfms_fix")
        print(fix_csv)
        df.to_csv(fix_csv,index=False)
        df0 = None
        df0 = df
        df = None
    return



def main():
    GFMS_list = ["Flood_byStor_2020051600.bin",
        "Flood_byStor_2020051603.bin",
        "Flood_byStor_2020051606.bin",
        "Flood_byStor_2020051609.bin",
        "Flood_byStor_2020051612.bin",
        "Flood_byStor_2020051615.bin",
        "Flood_byStor_2020051618.bin",
        "Flood_byStor_2020051621.bin",
        "Flood_byStor_2020051700.bin",
        "Flood_byStor_2020051703.bin",
        "Flood_byStor_2020051706.bin",
        "Flood_byStor_2020051709.bin",
        "Flood_byStor_2020051712.bin",
        "Flood_byStor_2020051715.bin",
        "Flood_byStor_2020051718.bin",
        "Flood_byStor_2020051721.bin",
        "Flood_byStor_2020051800.bin",
        "Flood_byStor_2020051803.bin",
        "Flood_byStor_2020051806.bin",
        "Flood_byStor_2020051809.bin",
        "Flood_byStor_2020051812.bin",
        "Flood_byStor_2020051815.bin",
        "Flood_byStor_2020051818.bin",
        "Flood_byStor_2020051821.bin",
        "Flood_byStor_2020051900.bin",
        "Flood_byStor_2020051903.bin",
        "Flood_byStor_2020051906.bin",
        "Flood_byStor_2020051909.bin",
        "Flood_byStor_2020051912.bin",
        "Flood_byStor_2020051915.bin",
        "Flood_byStor_2020051918.bin",
        "Flood_byStor_2020051921.bin",
        "Flood_byStor_2020052000.bin",
        "Flood_byStor_2020052003.bin",
        "Flood_byStor_2020052006.bin",
        "Flood_byStor_2020052009.bin",
        "Flood_byStor_2020052012.bin",
        "Flood_byStor_2020052015.bin",
        "Flood_byStor_2020052018.bin",
        "Flood_byStor_2020052021.bin",
        "Flood_byStor_2020052100.bin",
        "Flood_byStor_2020052103.bin",
        "Flood_byStor_2020052106.bin",
        "Flood_byStor_2020052109.bin",
        "Flood_byStor_2020052112.bin",
        "Flood_byStor_2020052115.bin",
        "Flood_byStor_2020052118.bin",
        "Flood_byStor_2020052121.bin",
        ]

    fix_duration(GFMS_list,folder="Amphan/gfms/")

if __name__ == "__main__":
    main()

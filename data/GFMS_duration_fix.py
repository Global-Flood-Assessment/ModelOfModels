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
        #print(df['pfaf_id'])
        #print(df0['pfaf_id'])
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
    GFMS_list = ["Flood_byStor_2020060821.csv",
"Flood_byStor_2020060900.csv",
"Flood_byStor_2020060903.csv",
"Flood_byStor_2020060906.csv",
"Flood_byStor_2020060909.csv",
"Flood_byStor_2020060912.csv",
"Flood_byStor_2020060915.csv",
"Flood_byStor_2020060918.csv",
"Flood_byStor_2020060921.csv",
"Flood_byStor_2020061000.csv",
"Flood_byStor_2020061003.csv",
"Flood_byStor_2020061006.csv",
"Flood_byStor_2020061009.csv",
"Flood_byStor_2020061012.csv",
"Flood_byStor_2020061015.csv",
"Flood_byStor_2020061018.csv",
"Flood_byStor_2020061021.csv",
"Flood_byStor_2020061100.csv",
"Flood_byStor_2020061103.csv",
"Flood_byStor_2020061106.csv",
"Flood_byStor_2020061109.csv",
"Flood_byStor_2020061112.csv",
"Flood_byStor_2020061115.csv",
"Flood_byStor_2020061118.csv",
"Flood_byStor_2020061121.csv",
"Flood_byStor_2020061200.csv",
"Flood_byStor_2020061203.csv",
"Flood_byStor_2020061206.csv",
"Flood_byStor_2020061209.csv",
"Flood_byStor_2020061212.csv",
"Flood_byStor_2020061215.csv",
"Flood_byStor_2020061218.csv",
"Flood_byStor_2020061221.csv",
"Flood_byStor_2020061300.csv",
"Flood_byStor_2020061303.csv",
"Flood_byStor_2020061306.csv",
"Flood_byStor_2020061309.csv",
"Flood_byStor_2020061312.csv",
"Flood_byStor_2020061315.csv",
"Flood_byStor_2020061318.csv",
"Flood_byStor_2020061321.csv",
"Flood_byStor_2020061400.csv",
"Flood_byStor_2020061403.csv",
"Flood_byStor_2020061406.csv",
"Flood_byStor_2020061409.csv",
"Flood_byStor_2020061412.csv",
"Flood_byStor_2020061415.csv",
"Flood_byStor_2020061418.csv",
"Flood_byStor_2020061421.csv",
"Flood_byStor_2020061500.csv",
"Flood_byStor_2020061503.csv",
"Flood_byStor_2020061506.csv",
"Flood_byStor_2020061509.csv",
"Flood_byStor_2020061512.csv",
"Flood_byStor_2020061515.csv",
"Flood_byStor_2020061518.csv",
"Flood_byStor_2020061521.csv",
"Flood_byStor_2020061600.csv",
"Flood_byStor_2020061603.csv",
#"Flood_byStor_2020061606.csv",
"Flood_byStor_2020061609.csv",
"Flood_byStor_2020061612.csv",
"Flood_byStor_2020061615.csv",
"Flood_byStor_2020061618.csv",
"Flood_byStor_2020061621.csv",
        ]
    fix_duration(GFMS_list,folder="testdata/gfms/")

if __name__ == "__main__":
    main()

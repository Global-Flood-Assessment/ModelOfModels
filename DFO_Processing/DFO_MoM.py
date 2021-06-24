"""
    DFO_MoM.py
        -- update Mom with DFO
"""

import csv
import pandas as pd
import os
import scipy.stats
import numpy as np

# data file
#DFO_20210618.csv
#Final_Attributes_20210618.csv
#Attributes_Clean_20200618.csv

def read_data(file):
    df = pd.read_csv(file)
    df = pd.DataFrame(df)
    return df

def mofunc(row):
    if row['Severity'] > 0.8 or row['Hazard_Score'] > 80:
        return 'Warning'
    elif 0.6 < row['Severity'] < 0.80 or 60 < row['Hazard_Score'] < 80:
        return 'Watch'
    elif 0.35 < row['Severity'] < 0.6 or 35 < row['Hazard_Score'] < 60:
        return 'Advisory'
    else:
        return 'Information'

def update_DFO_MoM(datestr):
    ''' update MoM - DFO at a given date '''

    MOMOutput='Final_Attributes_'+ datestr +'18.csv'
    DFO="DFO_"+ datestr +'.csv'

    weightage = read_data('weightage_DFO.csv')
    Attributes=read_data('Attributes.csv')
    PDC_resilience = read_data('Copy of Resilience_Index.csv')
    add_field_DFO=['DFO_area_1day_score', 'DFO_percarea_1day_score', 'DFO_area_2day_score', 'DFO_percarea_2day_score','DFO_area_3day_score', 'DFO_percarea_3day_score','DFOTotal_Score']


def main():
    testdate = "20210618"
    update_DFO_MoM(testdate)

if __name__ == "__main__":
    main()
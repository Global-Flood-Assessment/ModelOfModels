"""
    VIIRS_MoM.py
        -- update Mom with VIIRS
        -- Read  Final_Attributes_yyyymmddhh_MOM+DFOUpdated.csv as MOM+DFO File as MOM File and VIIRS_Flood_yyyymmdd.csv as VIIRS File. 
        -- Write the output Final_Attributes_yyyymmddhhMOM+DFO+VIIRSUpdated.csv and Attributes_clean_yyyymmddhhMOM+DFO+VIIRSUpdated.csv file.
"""

import csv,sys
import pandas as pd
import os
import scipy.stats
import numpy as np

def read_data(file):
    df = pd.read_csv(file)
    df = pd.DataFrame(df)
    return df

def mofunc_viirs(row):
    if row['Severity'] > 0.8 or row['Hazard_Score'] > 80:
        return 'Warning'
    elif 0.6 < row['Severity'] < 0.80 or 60 < row['Hazard_Score'] < 80:
        return 'Watch'
    elif 0.35 < row['Severity'] < 0.6 or 35 < row['Hazard_Score'] < 60:
        return 'Advisory'
    elif 0 < row['Severity'] < 0.35 or 0 < row['Hazard_Score'] < 35:
        return 'Information'


def update_VIIRS_MoM(adate,VIIRSf,DFO_MoMf,Outputf):
    """ update VIIRS_MoM """

    #input files
    hh = '18'
    DFO_MOMOutput = "Final_Attributes_{}{}MOM+DFOUpdated.csv".format(adate,hh)
    DFO_MOMOutput = DFO_MoMf + DFO_MOMOutput
    if not os.path.exists(DFO_MOMOutput):
        print("no file: ", DFO_MOMOutput)
        return

    VIIRS_summary_csv = "VIIRS_Flood_{}.csv".format(adate)
    VIIRS_summary_csv = VIIRSf + VIIRS_summary_csv
    if not os.path.exists(VIIRS_summary_csv):
        print("no file:",VIIRS_summary_csv)
        return
    
    #output files
    Final_Attributes_csv = "Final_Attributes_{}{}MOM+DFO+VIIRSUpdated.csv".format(adate,hh)
    Final_Attributes_csv = Outputf + Final_Attributes_csv
    Attributes_Clean_csv = "Attributes_clean_{}{}MOM+DFO+VIIRSUpdated.csv".format(adate,hh)
    Attributes_Clean_csv = Outputf + Attributes_Clean_csv

    #already processed
    if (os.path.exists(Final_Attributes_csv) and (Attributes_Clean_csv)):
        print('already processed: ',adate)
        return 

    weightage = read_data('VIIRS_Weightages.csv')
    Attributes=read_data('Attributes.csv')
    PDC_resilience = read_data('Copy of Resilience_Index.csv')
    add_field_VIIRS=['VIIRS_area_1day_score', 'VIIRS_percarea_1day_score', 'VIIRS_area_5day_score', 'VIIRS_percarea_5day_score','VIIRSTotal_Score']

    #Read VIIRS Processing data and calculate score
    with open(VIIRS_summary_csv, 'r', encoding='UTF-8') as VIIRS_file:
        VIIRS_reader = csv.reader(VIIRS_file)
        VIIRS_w_score_csv ="VIIRS_w_score_{}.csv".format(adate)
        csvfile = open(VIIRS_w_score_csv, 'w', newline='\n', encoding='utf-8')
        VIIRS_w_score = csv.writer(csvfile)
        row_count = 1
        # csv_writer = csv.writer(write_obj)
        for row in VIIRS_reader:
            if row_count == 1:
                for x in add_field_VIIRS:
                    row.append(x)
                row_count = row_count + 1
            else:
                if float(row[1]) / float(weightage.VIIRS_Area_wt) > float(weightage.VIIRS_Area_max_pt):
                    VIIRS_area_1day_score = str(float(weightage.VIIRS_Area_max_pt)*float(weightage.one_Day_Multiplier))
                else:
                    VIIRS_area_1day_score = str(float(weightage.VIIRS_Area_Min_pt) * float(weightage.one_Day_Multiplier)* float(row[1]) / float(weightage.VIIRS_Area_wt))
                if float(row[2]) / float(weightage.VIIRS_percArea_wt) > float(weightage.VIIRS_percArea_Maxpt):
                    VIIRS_perc_area_1day_score = str(float(weightage.VIIRS_percArea_Maxpt)*float(weightage.one_Day_Multiplier))
                else:
                    VIIRS_perc_area_1day_score = str(float(weightage.VIIRS_percArea_Minpt)*float(weightage.one_Day_Multiplier)* float(row[2]) / float(weightage.VIIRS_percArea_wt))
                if float(row[3]) / float(weightage.VIIRS_Area_wt) > float(weightage.VIIRS_Area_max_pt):
                    VIIRS_area_5day_score = str(float(weightage.VIIRS_Area_max_pt)*float(weightage.five_Day_Multiplier))
                else:
                    VIIRS_area_5day_score = str(float(weightage.VIIRS_Area_Min_pt) * float(weightage.five_Day_Multiplier)* float(row[3]) / float(weightage.VIIRS_Area_wt))
                if float(row[4]) / float(weightage.VIIRS_percArea_wt) > float(weightage.VIIRS_percArea_Maxpt):
                    VIIRS_perc_area_5day_score = str(float(weightage.VIIRS_percArea_Maxpt)*float(weightage.five_Day_Multiplier))
                else:
                    VIIRS_perc_area_5day_score = str(float(weightage.VIIRS_percArea_Minpt)*float(weightage.five_Day_Multiplier)* float(row[4]) / float(weightage.VIIRS_percArea_wt))          
                Sum_Score = str(
                    (float(VIIRS_area_1day_score) + float(VIIRS_perc_area_1day_score) + float(VIIRS_area_5day_score) + float(VIIRS_perc_area_5day_score)))
                score_field = [VIIRS_area_1day_score, VIIRS_perc_area_1day_score, VIIRS_area_5day_score, VIIRS_perc_area_5day_score, Sum_Score]
                for x in score_field:
                    row.append(x)
            VIIRS_w_score.writerow(row)
    csvfile.close()

    VIIRS = read_data(VIIRS_w_score_csv)
    VIIRS = VIIRS[VIIRS.VIIRSTotal_Score > 0.1]
    MOM = read_data(DFO_MOMOutput)
    MOM.drop(columns=['area_km2','ISO','Admin0','Admin1','rfr_score','cfr_score','Resilience_Index',' NormalizedLackofResilience ','Severity','Alert'], inplace=True)
    Final_Output_0= pd.merge(MOM.set_index('pfaf_id'), VIIRS.set_index('pfaf_id'), on='pfaf_id', how='outer')
    join1 = pd.merge(Attributes, PDC_resilience[['ISO', 'Resilience_Index', ' NormalizedLackofResilience ']], on='ISO', how='inner')
    Final_Output=pd.merge(join1.set_index('pfaf_id'), Final_Output_0, on='pfaf_id', how='right')
    Final_Output[['Hazard_Score']] = Final_Output[['Hazard_Score']].fillna(value=0)
    Final_Output.loc[(Final_Output['Hazard_Score']<Final_Output['VIIRSTotal_Score']),'Flag']=3
    Final_Output['Hazard_Score'] =Final_Output[['Hazard_Score', 'VIIRSTotal_Score']].max(axis=1)
    Final_Output = Final_Output[Final_Output.Hazard_Score != 0]
    Final_Output.drop(Final_Output.index[(Final_Output['rfr_score']==0) & (Final_Output['cfr_score']==0)], inplace=True)
    Final_Output = Final_Output.assign(
        Scaled_Riverine_Risk=lambda x: Final_Output['rfr_score'] * 20)
    Final_Output = Final_Output.assign(
        Scaled_Coastal_Risk=lambda x: Final_Output['cfr_score'] * 20)
    Final_Output = Final_Output.assign(
        Severity=lambda x: scipy.stats.norm(np.log(100 - Final_Output[['Scaled_Riverine_Risk', 'Scaled_Coastal_Risk']].max(axis=1)), 1).cdf(
            np.log(Final_Output['Hazard_Score'])))
    Final_Output['Alert'] = Final_Output.apply(mofunc_viirs, axis=1)
    Final_Output.loc[Final_Output['Alert']=="Information",'Flag']=''
    Final_Output.loc[Final_Output['Alert']=="Advisory",'Flag']=''
    Final_Output.to_csv(Final_Attributes_csv, encoding='utf-8-sig')
    join1 = pd.merge(Attributes, PDC_resilience[['ISO', 'Resilience_Index', ' NormalizedLackofResilience ']], on='ISO', how='inner')
    Attributes_Clean_VIIRS_Updated = pd.merge(join1.set_index('pfaf_id'), Final_Output[['Alert','Flag']], on='pfaf_id', how='right')
    Attributes_Clean_VIIRS_Updated.to_csv(Attributes_Clean_csv, encoding='utf-8-sig')
    os.remove(VIIRS_w_score_csv)

    return

def batchrun():

    home = os.path.expanduser("~")
    if os.path.exists(home + "/Projects"):
        home = home + "/Projects"
    DFO_MoM_folder = home + "/ModelofModels/data/cron_data/DFO/DFO_MoM/"
    VIIRS_folder = home + "/ModelofModels/data/cron_data/VIIRS/VIIRS_summary/"
    Output_folder = home + "/ModelofModels/data/cron_data/VIIRS/VIIRS_MoM/"

    #adate = '20210829'
    #update_VIIRS_MoM(adate,VIIRS_folder, DFO_MoM_folder,Output_folder)


    alist = os.listdir(VIIRS_folder)
    alist.sort()
    for item in alist:
        if not '.csv' in item:
            continue
        datestr = item[:-4].split('_')[-1]
        print('Processing: ', datestr)
        update_VIIRS_MoM(datestr,VIIRS_folder, DFO_MoM_folder,Output_folder)

def main():
    batchrun()

if __name__ == "__main__":
    main()
"""
    DFO_MoM.py
        -- update Mom with DFO
        -- Read Final_Attributes_yyyymmddhhHWRFUpdated.csv as MOM File and DFO_yyyymmdd.csv as DFO File. 
        -- Write the output Final_Attributes_yyyymmddhhMOM+DFOUpdated.csv and Attributes_clean_yyyymmddhhMOM+DFOUpdated.csv file. 
"""

import csv
import pandas as pd
import os
import scipy.stats
import numpy as np
import glob

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
    elif 0 < row['Severity'] < 0.35 or 0 < row['Hazard_Score'] < 35:
        return 'Information'

def update_DFO_MoM(adate,DFOfolder,MoMfolder,Outputfolder):
    ''' update MoM - DFO at a given date '''

    hh = "18"
    MOMOutput= MoMfolder + 'Final_Attributes_{}{}HWRFUpdated.csv'.format(adate,hh)
    DFO= DFOfolder + "DFO_"+ adate +'.csv'

    #output
    #Final_Attributes_yyyymmddhhMOM+DFOUpdated.csv
    #Attributes_clean_yyyymmddhhMOM+DFOUpdated.csv 
    Final_Attributes_csv = Outputfolder + 'Final_Attributes_{}{}MOM+DFOUpdated.csv'.format(adate,hh)
    Attributes_Clean_csv = Outputfolder + 'Attributes_Clean_{}{}MOM+DFOUpdated.csv'.format(adate,hh)

    weightage = read_data('weightage_DFO.csv')
    Attributes=read_data('Attributes.csv')
    PDC_resilience = read_data('Copy of Resilience_Index.csv')
    add_field_DFO=['DFO_area_1day_score', 'DFO_percarea_1day_score', 'DFO_area_2day_score', 'DFO_percarea_2day_score','DFO_area_3day_score', 'DFO_percarea_3day_score','DFOTotal_Score']

    #Read DFO Processing data and calculate score
    with open(DFO, 'r', encoding='UTF-8') as DFO_file:
        DFO_reader = csv.reader(DFO_file)
        DFO_w_score_csv = "DFO_w_score_{}.csv".format(adate)
        csvfile = open(DFO_w_score_csv, 'w', newline='\n', encoding='utf-8')
        DFO_w_score = csv.writer(csvfile)
        row_count = 1
        # csv_writer = csv.writer(write_obj)
        for row in DFO_reader:
            if row_count == 1:
                for x in add_field_DFO:
                    row.append(x)
                row_count = row_count + 1
            else:
                if float(row[4]) / float(weightage.DFO_Area_wt) > float(weightage.DFO_Area_max_pt):
                    DFO_area_1day_score = str(float(weightage.DFO_Area_max_pt)*float(weightage.one_Day_Multiplier))
                else:
                    DFO_area_1day_score = str(float(weightage.DFO_Area_Min_pt) * float(weightage.one_Day_Multiplier)* float(row[4]) / float(weightage.DFO_Area_wt))
                if float(row[5]) / float(weightage.DFO_percArea_wt) > float(weightage.DFO_percArea_Maxpt):
                    DFO_perc_area_1day_score = str(float(weightage.DFO_percArea_Maxpt)*float(weightage.one_Day_Multiplier))
                else:
                    DFO_perc_area_1day_score = str(float(weightage.DFO_percArea_Minpt)*float(weightage.one_Day_Multiplier)* float(row[5]) / float(weightage.DFO_percArea_wt))
                if float(row[6]) / float(weightage.DFO_Area_wt) > float(weightage.DFO_Area_max_pt):
                    DFO_area_2day_score = str(float(weightage.DFO_Area_max_pt)*float(weightage.two_Day_Multiplier))
                else:
                    DFO_area_2day_score = str(float(weightage.DFO_Area_Min_pt) * float(weightage.two_Day_Multiplier)* float(row[6]) / float(weightage.DFO_Area_wt))
                if float(row[7]) / float(weightage.DFO_percArea_wt) > float(weightage.DFO_percArea_Maxpt):
                    DFO_perc_area_2day_score = str(float(weightage.DFO_percArea_Maxpt)*float(weightage.two_Day_Multiplier))
                else:
                    DFO_perc_area_2day_score = str(float(weightage.DFO_percArea_Minpt)*float(weightage.two_Day_Multiplier)* float(row[7]) / float(weightage.DFO_percArea_wt))
                if float(row[8]) / float(weightage.DFO_Area_wt) > float(weightage.DFO_Area_max_pt):
                    DFO_area_3day_score = str(float(weightage.DFO_Area_max_pt)*float(weightage.three_Day_Multiplier))
                else:
                    DFO_area_3day_score = str(float(weightage.DFO_Area_Min_pt) * float(weightage.three_Day_Multiplier)* float(row[8]) / float(weightage.DFO_Area_wt))
                if float(row[9]) / float(weightage.DFO_percArea_wt) > float(weightage.DFO_percArea_Maxpt):
                    DFO_perc_area_3day_score = str(float(weightage.DFO_percArea_Maxpt)*float(weightage.three_Day_Multiplier))
                else:
                    DFO_perc_area_3day_score = str(float(weightage.DFO_percArea_Minpt)*float(weightage.three_Day_Multiplier)* float(row[9]) / float(weightage.DFO_percArea_wt))
                                            
                Sum_Score = str(
                    (float(DFO_area_1day_score) + float(DFO_perc_area_1day_score) + float(DFO_area_2day_score) + float(DFO_perc_area_2day_score)+float(DFO_area_3day_score) + float(DFO_perc_area_3day_score)))
                score_field = [DFO_area_1day_score, DFO_perc_area_1day_score, DFO_area_2day_score, DFO_perc_area_2day_score, DFO_area_3day_score, DFO_perc_area_3day_score,Sum_Score]
                for x in score_field:
                    row.append(x)
            DFO_w_score.writerow(row)
    csvfile.close()

    DFO = read_data(DFO_w_score_csv)
    DFO = DFO[DFO.DFOTotal_Score > 0.1]
    DFO = DFO.iloc[:,1:]
    MOM = read_data(MOMOutput)
    MOM.drop(columns=['area_km2','ISO','Admin0','Admin1','rfr_score','cfr_score','Resilience_Index',' NormalizedLackofResilience ','Severity','Alert'], inplace=True)
    Final_Output_0= pd.merge(MOM.set_index('pfaf_id'), DFO.set_index('pfaf_id'), on='pfaf_id', how='outer')
    join1 = pd.merge(Attributes, PDC_resilience[['ISO', 'Resilience_Index', ' NormalizedLackofResilience ']], on='ISO', how='inner')
    Final_Output=pd.merge(join1.set_index('pfaf_id'), Final_Output_0, on='pfaf_id', how='outer')
    Final_Output[['Hazard_Score']] = Final_Output[['Hazard_Score']].fillna(value=0)
    Final_Output.loc[(Final_Output['Hazard_Score']<Final_Output['DFOTotal_Score']),'Flag']=2
    Final_Output['Hazard_Score'] =Final_Output[['Hazard_Score', 'DFOTotal_Score']].max(axis=1)
    Final_Output = Final_Output[Final_Output.Hazard_Score != 0]
    Final_Output.drop(Final_Output.index[(Final_Output['rfr_score']==0) & (Final_Output['cfr_score']==0)], inplace=True)
    Final_Output = Final_Output.assign(
        Scaled_Riverine_Risk=lambda x: Final_Output['rfr_score'] * 20)
    Final_Output = Final_Output.assign(
        Scaled_Coastal_Risk=lambda x: Final_Output['cfr_score'] * 20)
    Final_Output = Final_Output.assign(
        Severity=lambda x: scipy.stats.norm(np.log(100 - Final_Output[['Scaled_Riverine_Risk', 'Scaled_Coastal_Risk']].max(axis=1)), 1).cdf(
            np.log(Final_Output['Hazard_Score'])))
    Final_Output['Alert'] = Final_Output.apply(mofunc, axis=1)
    Final_Output.loc[Final_Output['Alert']=="Information",'Flag']=''
    Final_Output.loc[Final_Output['Alert']=="Advisory",'Flag']=''
    Final_Output.to_csv(Final_Attributes_csv, encoding='utf-8-sig')
    #Final_Output.to_csv('Final_Attributes_20210701_DFOUpdated.csv', encoding='utf-8-sig')
    join1 = pd.merge(Attributes, PDC_resilience[['ISO', 'Resilience_Index', ' NormalizedLackofResilience ']], on='ISO', how='inner')
    Attributes_Clean_DFO_Updated = pd.merge(join1.set_index('pfaf_id'), Final_Output[['Alert','Flag']], on='pfaf_id', how='right')
    Attributes_Clean_DFO_Updated.to_csv(Attributes_Clean_csv, encoding='utf-8-sig')
    os.remove(DFO_w_score_csv)

    return

def batchrun():

    home = os.path.expanduser("~")
    DFO_folder = home + "/Projects/ModelOfModels/data/cron_data/DFO/DFO_summary/"
    MoM_folder = home + "/Projects/ModelOfModels/data/cron_data/HWRF/HWRF_MoM/"
    Output_folder = home + "/Projects/ModelOfModels/data/cron_data/DFO/DFO_MoM/"

    adate = '20210829'
    update_DFO_MoM(adate,DFO_folder,MoM_folder,Output_folder)

    # alist = os.listdir(DFO_folder)
    # alist.sort()
    # for item in alist:
    #     if not '.csv' in item:
    #         continue
    #     datestr = item[:-4].split('_')[1]
    #     print('Processing: ', datestr)
    #     update_DFO_MoM(datestr,DFO_folder,MoM_folder,Output_folder)

def main():
    #testdate = "20210618"
    #update_DFO_MoM(testdate)
    batchrun()

if __name__ == "__main__":
    main()
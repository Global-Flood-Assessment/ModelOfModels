"""
    HWRF_MoM.py
        -- HWRF and MoM integration
"""

import csv
import pandas as pd
import os
import scipy.stats
import numpy as np
from datetime import date,timedelta,datetime
import glob

def read_data(file):
    df = pd.read_csv(file)
    df = pd.DataFrame(df)
    return df

def mofunc_hwrf(row):
    if row['Severity'] > 0.8 or row['Hazard_Score'] > 80:
        return 'Warning'
    elif 0.6 < row['Severity'] < 0.80 or 60 < row['Hazard_Score'] < 80:
        return 'Watch'
    elif 0.35 < row['Severity'] < 0.6 or 35 < row['Hazard_Score'] < 60:
        return 'Advisory'
    elif 0 < row['Severity'] < 0.35 or 0 < row['Hazard_Score'] < 35:
        return 'Information'

def update_HWRF_MoM(adate,gfmsfolder,glofasfolder,hwrffolder,outputfolder):
    """ HWRF MoM for a date: YYYYMMDDHH"""

    #GFMS="Flood_byStor_2021070106.csv"
    #GloFas="threspoints_2021070100.csv"
    #HWRF="hwrf.2021070106rainfall.csv"
    GFMS = "Flood_byStor_" + adate + ".csv"
    GloFas = "threspoints_" + adate[:-2] + "00.csv"
    HWRF = "hwrf." + adate + "rainfall.csv"

    # first check if file exists
    if not os.path.exists(gfmsfolder+GFMS):
        return
    if not os.path.exists(glofasfolder + GloFas):
        return
    # if not os.path.exists(hwrffolder + HWRF):
    #     return
    
    GFMS = gfmsfolder + GFMS
    GloFas = glofasfolder + GloFas
    HWRF = hwrffolder + HWRF

    Final_Attributes_csv = outputfolder + 'Final_Attributes_{}HWRFUpdated.csv'.format(adate)
    Attributes_Clean_csv = outputfolder + 'Attributes_Clean_{}HWRFUpdated.csv'.format(adate)

    #already processed
    if (os.path.exists(Final_Attributes_csv) and (Attributes_Clean_csv)):
        print('already processed: ',adate)
        return 

    weightage = read_data('Weightage.csv')
    HWRF_weightage = read_data('HWRF_Weightage.csv')
    add_field_GloFas = ['Alert_Score', 'PeakArrivalScore', 'TwoYScore', 'FiveYScore', 'TwtyYScore', 'Sum_Score']
    add_field_GFMS = ['GFMS_area_score', 'GFMS_perc_area_score', 'MeanD_Score', 'MaxD_Score', 'Duration_Score', 'Sum_Score']
    add_field_HWRF=['HWRF_area_score', 'HWRF_percarea_score', 'MeanRain_Score', 'MaxRain_Score', 'HWRFTot_Score']

    #Read GFMS Processing data and calculte score
    with open(GFMS, 'r', encoding='UTF-8') as GFMS_file:
        GFMS_reader = csv.reader(GFMS_file)
        GFMS_w_score_csv = "GFMS_w_score_{}.csv".format(adate)
        csvfile = open(GFMS_w_score_csv, 'w', newline='\n', encoding='utf-8')
        GFMS_w_score = csv.writer(csvfile)
        row_count = 1
        # csv_writer = csv.writer(write_obj)
        for row in GFMS_reader:
            if row_count == 1:
                for x in add_field_GFMS:
                    row.append(x)
                row_count = row_count + 1
            else:
                if float(row[1]) / float(weightage.GFMS_Area_wt) > float(weightage.GFMS_Area_max_pt):
                    GFMS_area_score = str(float(weightage.GFMS_Area_max_pt))
                else:
                    GFMS_area_score = str(float(weightage.GFMS_Area_Min_pt) * float(row[1]) / float(weightage.GFMS_Area_wt))
                if float(row[2]) / float(weightage.GFMS_percArea_wt) > float(weightage.GFMS_percArea_Maxpt):
                    GFMS_perc_area_score = str(float(weightage.GFMS_percArea_Maxpt))
                else:
                    GFMS_perc_area_score = str(float(weightage.GFMS_percArea_Minpt) * float(row[2]) / float(weightage.GFMS_percArea_wt))
                if float(row[3]) / float(weightage.GFMS_Meandepth_wt) > float(weightage.GFMS_Meandepth_Maxpt):
                    MeanD_Score = str(float(weightage.GFMS_Meandepth_Maxpt))
                else:
                    MeanD_Score = str(float(weightage.GFMS_Meandepth_Minpt)*float(row[3]) / float(weightage.GFMS_Meandepth_wt))
                if float(row[4]) / float(weightage.GFMS_Maxdepth_wt) > float(weightage.GFMS_Maxdepth_Maxpt):
                    MaxD_Score = str(float(weightage.GFMS_Maxdepth_Maxpt))
                else:
                    MaxD_Score = str(float(weightage.GFMS_Maxdepth_Minpt) * float(row[4]) / float(weightage.GFMS_Maxdepth_wt))
                if float(row[5]) / float(weightage.GFMS_Duration_wt) > float(weightage.GFMS_Duration_Maxpt):
                    Duration_Score = str(float(weightage.GFMS_Duration_Maxpt))
                else:
                    Duration_Score = str(float(weightage.GFMS_Duration_Minpt) * float(row[5]) / float(weightage.GFMS_Duration_wt))
                Sum_Score = str(
                    float(GFMS_area_score) + float(GFMS_perc_area_score) + float(MeanD_Score) + float(MaxD_Score) + float(
                        Duration_Score))
                score_field = [GFMS_area_score, GFMS_perc_area_score, MeanD_Score, MaxD_Score, Duration_Score, Sum_Score]
                for x in score_field:
                    row.append(x)
            GFMS_w_score.writerow(row)
    csvfile.close()

    ##Read GloFas data and Calculate score
    with open(GloFas, 'r', encoding='UTF-8') as GloFas_file:
        GloFas_reader = csv.reader(GloFas_file)
        GloFas_w_score_csv = "GloFas_w_score_{}.csv".format(adate)
        GloFas_Error_csv = "GloFas_Error_{}.csv".format(adate)
        csvfile = open(GloFas_w_score_csv, 'w', newline='\n', encoding='utf-8')
        txtfile = open(GloFas_Error_csv, 'w', newline='\n')
        GloFas_w_score = csv.writer(csvfile)
        errorfile = csv.writer(txtfile)
        row_count = 1
        error_flag = False
        for row in GloFas_reader:
            if row_count == 1:
                for x in add_field_GloFas:
                    row.append(x)
                write = [row[14], row[12], row[13], row[9], row[10], row[11], row[15], row[16], row[17], row[18], row[19],
                        row[20]]
                GloFas_w_score.writerow(write)
                errorfile.writerow([row[0], row[1], row[14], 'Error'])
                row_count = row_count + 1
            elif float(row[12]) > 3 or float(row[12]) < 0:
                error = "Alert less than 0 or greater than 3 is encountered"
                errorfile.writerow([row[0], row[1], row[14], error])
                error_flag = True
            elif float(row[9]) > 100:
                error = "2 yr EPS greater than 100 is encountered"
                errorfile.writerow([row[0], row[1], row[14], error])
                error_flag = True
            elif float(row[10]) > 100:
                error = "5 yr EPS greater than 100 is encountered"
                errorfile.writerow([row[0], row[1], row[14], error])
                error_flag = True
            elif float(row[11]) > 100:
                error = "20 yr EPS greater than 100 is encountered"
                errorfile.writerow([row[0], row[1], row[14], error])
                error_flag = True
            elif float(row[13]) > 30:
                error = "Peak arrival days greater than 30 is encountered"
                errorfile.writerow([row[0], row[1], row[14], error])
                error_flag = True
            else:
                Alert_Score = str(round(float(row[12]) * float(weightage.Alert_score)))
                TwoYScore = str(float(row[9]) / float(weightage.EPS_Twoyear_wt))
                FiveYScore = str(float(row[10]) / float(weightage.EPS_Fiveyear_wt))
                TwtyYScore = str(float(row[11]) / float(weightage.EPS_Twtyyear_wt))
                if int(row[9]) == 0 and int(row[10]) == 0 and int(row[11]) == 0 and int(row[12]) == 0:
                    PeakArrival_Score = str(0)
                elif int(row[13]) == 10 or int(row[13]) > 10:
                    PeakArrival_Score = str(1)
                elif int(row[13]) == 9:
                    PeakArrival_Score = str(2)
                elif int(row[13]) == 8:
                    PeakArrival_Score = str(3)
                elif int(row[13]) == 7:
                    PeakArrival_Score = str(4)
                elif int(row[13]) == 6:
                    PeakArrival_Score = str(5)
                elif int(row[13]) == 5:
                    PeakArrival_Score = str(6)
                elif int(row[13]) == 4:
                    PeakArrival_Score = str(7)
                elif int(row[13]) == 3:
                    PeakArrival_Score = str(8)
                elif int(row[13]) == 2:
                    PeakArrival_Score = str(9)
                elif int(row[13]) == 1:
                    PeakArrival_Score = str(10)
                Sum_Score = str(
                    float(Alert_Score) + float(PeakArrival_Score) + float(TwoYScore) + float(FiveYScore) + float(
                        TwtyYScore))
                score_field = [Alert_Score, PeakArrival_Score, TwoYScore, FiveYScore, TwtyYScore, Sum_Score]
                for x in score_field:
                    row.append(x)
                write = [row[14], row[12], row[13], row[9], row[10], row[11], row[15], row[16], row[17], row[18], row[19],
                    row[20]]
                GloFas_w_score.writerow(write)
    csvfile.close()
    txtfile.close()
    if not error_flag:
        os.remove(GloFas_Error_csv)
    GloFas = read_data(GloFas_w_score_csv)
    GloFas.sort_values(by='pfaf_id', ascending=True, inplace=True)
    GloFas_w_score_sort_csv = "GloFas_w_score_sort_{}.csv".format(adate)
    GloFas.set_index('pfaf_id').to_csv(GloFas_w_score_sort_csv, encoding='utf-8')

    with open(GloFas_w_score_sort_csv, 'r') as GloFas_file:
        GloFas_reader = csv.reader(GloFas_file)
        GloFas_w_Avgscore_csv = "GloFas_w_Avgscore_{}.csv".format(adate)
        csvfile = open(GloFas_w_Avgscore_csv, 'w', newline='\n', encoding='utf-8')
        GloFas_w_score = csv.writer(csvfile)
        Haz_Score = 0
        pfaf_id = -1
        similarity = 0
        i = 1
        To_be_written = 'False'
        write = []
        for row in GloFas_reader:
            if i == 1:
                i = i + 1
                GloFas_w_score.writerow(row)
            else:
                if pfaf_id == -1 or pfaf_id == row[0]:
                    pfaf_id = row[0]
                    Haz_Score = Haz_Score + float(row[11])
                    similarity = similarity + 1
                    last_row = row
                    To_be_written = 'True'
                else:
                    last_row[11] = str(Haz_Score / similarity)
                    GloFas_w_score.writerow(last_row)
                    last_row = row
                    pfaf_id = row[0]
                    Haz_Score = float(row[11])
                    similarity = 1
                    To_be_written = 'True'
    if To_be_written == 'True':
        last_row[11] = str(Haz_Score / similarity)
        GloFas_w_score.writerow(last_row)
    csvfile.close()
    # Glofas Done
    os.remove(GloFas_w_score_sort_csv)

    ## Read HWRF rainfall processed data and calculate separate hazard Score
    try:
        with open(HWRF, 'r', encoding='UTF-8') as HWRF_file:
            HWRF_reader = csv.reader(HWRF_file)
            HWRF_w_score_csv = "HWRF_w_score_{}.csv".format(adate)
            csvfile = open(HWRF_w_score_csv, 'w', newline='\n', encoding='utf-8')
            HWRF_w_score = csv.writer(csvfile)
            row_count = 1
            # csv_writer = csv.writer(write_obj)
            for row in HWRF_reader:
                if row_count == 1:
                    for x in add_field_HWRF:
                        row.append(x)
                    HWRF_w_score.writerow(row)
                    row_count = row_count + 1
                elif row==[]:
                    continue
                else:
                    if float(row[1]) / float(HWRF_weightage.HWRF_Area_wt) > float(HWRF_weightage.HWRF_Area_max_pt):
                        HWRF_area_score = str(float(HWRF_weightage.HWRF_Area_max_pt))
                    else:
                        HWRF_area_score = str(float(HWRF_weightage.HWRF_Area_Min_pt) * float(row[1]) / float(HWRF_weightage.HWRF_Area_wt))
                    if float(row[2]) / float(HWRF_weightage.HWRF_percArea_wt) > float(HWRF_weightage.HWRF_percArea_Maxpt):
                        HWRF_percarea_score = str(float(HWRF_weightage.HWRF_percArea_Maxpt))
                    else:
                        HWRF_percarea_score = str(float(HWRF_weightage.HWRF_percArea_Minpt) * float(row[2]) / float(HWRF_weightage.HWRF_percArea_wt))
                    if float(row[3]) >= float(HWRF_weightage.HWRF_MeanRain_minwt):
                        if ((float(row[3])- float(HWRF_weightage.HWRF_MeanRain_minwt))/ float(HWRF_weightage.HWRF_MeanRain_increment))+float(HWRF_weightage.HWRF_MeanRain_Minpt) > float(HWRF_weightage.HWRF_MeanRain_Maxpt):
                            MeanRain_Score = str(float(HWRF_weightage.HWRF_MeanRain_Maxpt))
                        else:
                            MeanRain_Score = str(((float(row[3])- float(HWRF_weightage.HWRF_MeanRain_minwt))/ float(HWRF_weightage.HWRF_MeanRain_increment))+float(HWRF_weightage.HWRF_MeanRain_Minpt))
                    else:
                        MeanRain_Score='0'
                    if float(row[4]) >= float(HWRF_weightage.HWRF_MaxRain_minwt):                       
                        if ((float(row[4])- float(HWRF_weightage.HWRF_MaxRain_minwt))/ float(HWRF_weightage.HWRF_MaxRain_increment))+float(HWRF_weightage.HWRF_MaxRain_Minpt) > float(HWRF_weightage.HWRF_MaxRain_Maxpt):
                            MaxRain_Score = str(float(HWRF_weightage.HWRF_MaxRain_Maxpt))
                        else:
                            MaxRain_Score = str(((float(row[4])- float(HWRF_weightage.HWRF_MaxRain_minwt))/ float(HWRF_weightage.HWRF_MaxRain_increment))+float(HWRF_weightage.HWRF_MaxRain_Minpt))
                    else:
                        MaxRain_Score='0'
                    HWRFTot_Score = (float(HWRF_area_score)+float(HWRF_percarea_score)+ float(MeanRain_Score)+float(MaxRain_Score))*2.5 
                    results_list = [row[0], row[1], row[2], row[3], row[4],HWRF_area_score,HWRF_percarea_score,MeanRain_Score,MaxRain_Score, HWRFTot_Score]
                    HWRF_w_score.writerow(results_list)
    except:
        pass

    GFMS = read_data(GFMS_w_score_csv)
    GloFas = read_data(GloFas_w_Avgscore_csv)
    Attributes = read_data('Attributes.csv')
    #HWRF=read_data('HWRF_w_score.csv')
    join = pd.merge(GloFas.set_index('pfaf_id'), GFMS.set_index('pfaf_id'), on='pfaf_id', how='outer')
    #join0=pd.merge(join, HWRF.set_index('pfaf_id'), on='pfaf_id', how='outer')
    PDC_resilience = read_data('Copy of Resilience_Index.csv')
    join1 = pd.merge(Attributes, PDC_resilience[['ISO', 'Resilience_Index', ' NormalizedLackofResilience ']], on='ISO', how='inner')
    #Final_Attributes = pd.merge(join1.set_index('pfaf_id'), join0, on='pfaf_id', how='outer')
    Final_Attributes = pd.merge(join1.set_index('pfaf_id'), join, on='pfaf_id', how='outer')
    Final_Attributes[['Sum_Score_x', 'Sum_Score_y']] = Final_Attributes[['Sum_Score_x', 'Sum_Score_y']].fillna(value=0)
    Final_Attributes['Sum_Score_x'][(Final_Attributes['Sum_Score_y'] == 0)] = Final_Attributes['Sum_Score_x']*2
    Final_Attributes['Sum_Score_y'][(Final_Attributes['Sum_Score_x'] == 0)] = Final_Attributes['Sum_Score_y']*2
    Final_Attributes = Final_Attributes.assign(
        MOM_Score=lambda x: Final_Attributes['Sum_Score_x'] + Final_Attributes['Sum_Score_y'])
    Final_Attributes['Hazard_Score']=Final_Attributes[['MOM_Score']]
    try:
        HWRF=read_data(HWRF_w_score_csv)
        Final_Attributes=pd.merge(Final_Attributes, HWRF.set_index('pfaf_id'), on='pfaf_id', how='outer')
        Final_Attributes['Flag']=np.where((Final_Attributes['Hazard_Score']<Final_Attributes['HWRFTot_Score']),1,'')
        Final_Attributes['Hazard_Score'] =Final_Attributes[['Hazard_Score', 'HWRFTot_Score']].max(axis=1)
    except:
        pass
    Final_Attributes = Final_Attributes[Final_Attributes.Hazard_Score != 0]
    Final_Attributes.drop(Final_Attributes.index[(Final_Attributes['rfr_score']==0) & (Final_Attributes['cfr_score']==0)], inplace=True)
    Final_Attributes = Final_Attributes.assign(
        Scaled_Riverine_Risk=lambda x: Final_Attributes['rfr_score'] * 20)
    Final_Attributes = Final_Attributes.assign(
        Scaled_Coastal_Risk=lambda x: Final_Attributes['cfr_score'] * 20)
    Final_Attributes = Final_Attributes.assign(
        Severity=lambda x: scipy.stats.norm(np.log(100 - Final_Attributes[['Scaled_Riverine_Risk', 'Scaled_Coastal_Risk']].max(axis=1)), 1).cdf(
            np.log(Final_Attributes['Hazard_Score'])))
    Final_Attributes['Alert'] = Final_Attributes.apply(mofunc_hwrf, axis=1)
    Final_Attributes.loc[Final_Attributes['Alert']=="Information",'Flag']=''
    Final_Attributes.loc[Final_Attributes['Alert']=="Advisory",'Flag']=''
    Final_Attributes.to_csv(Final_Attributes_csv, encoding='utf-8-sig')
    #Final_Attributes.to_csv('Final_Attributes_2021081606.csv', encoding='utf-8-sig')
    Attributes_Clean = pd.merge(join1.set_index('pfaf_id'), Final_Attributes[['Alert']], on='pfaf_id', how='right')
    Attributes_Clean.to_csv(Attributes_Clean_csv, encoding='utf-8-sig')
    os.remove(GloFas_w_score_csv)
    os.remove(GloFas_w_Avgscore_csv)
    os.remove(GFMS_w_score_csv)
    try:
        os.remove(HWRF_w_score_csv)
    except:
        pass

def find_latest_summary(datestr, scanfolder,namepattern,hours):
    """ find the latest summary data"""

    # turn the datestr into a real date
    da = datetime.strptime(datestr,"%Y%m%d")
    startd = 1 
    if hours == '18':
        startd = 0
    # check the data
    for i in range(startd, 10):
        cdate = da - timedelta(days=i)
        cdatestr = cdate.strftime("%Y%m%d")
        cfile = scanfolder + namepattern.format(cdatestr)
        if os.path.exists(cfile):
            return [cdatestr, cfile]
    
    return

def mofunc_dfo(row):
    if row['Severity'] > 0.8 or row['Hazard_Score'] > 80:
        return 'Warning'
    elif 0.6 < row['Severity'] < 0.80 or 60 < row['Hazard_Score'] < 80:
        return 'Watch'
    elif 0.35 < row['Severity'] < 0.6 or 35 < row['Hazard_Score'] < 60:
        return 'Advisory'
    elif 0 < row['Severity'] < 0.35 or 0 < row['Hazard_Score'] < 35:
        return 'Information'

def mofunc_viirs(row):
    if row['Severity'] > 0.8 or row['Hazard_Score'] > 80:
        return 'Warning'
    elif 0.6 < row['Severity'] < 0.80 or 60 < row['Hazard_Score'] < 80:
        return 'Watch'
    elif 0.35 < row['Severity'] < 0.6 or 35 < row['Hazard_Score'] < 60:
        return 'Advisory'
    elif 0 < row['Severity'] < 0.35 or 0 < row['Hazard_Score'] < 35:
        return 'Information'

def update_HWRFMoM_DFO_VIIRS(adate,HWRF_f,DFO_f,VIIRS_f,outputdir):
    """
        update HWRFMoM with the latest available DFO and VIIRS 
    """
    
    # first check if it is produced
    hwrf_pattern = adate+"HWRF"
    file_list = os.listdir(outputdir)
    file_found = [1 for x in file_list if hwrf_pattern in x]
    if len(file_found) > 0:
        # this date is already processed
        return

    # adate 
    datestr = adate[:-2]
    hourstr = adate[-2:]
    [dfo_date,dfo_summary] = find_latest_summary(datestr,DFO_f,"DFO_{}.csv",hourstr)
    [viirs_date,viirs_summary] = find_latest_summary(datestr,VIIRS_f,"VIIRS_Flood_{}.csv",hourstr)

    # geneate HWRF_DFO_MoM
    MOMOutput= HWRF_f + 'Final_Attributes_{}HWRFUpdated.csv'.format(adate)
    if not os.path.exists(MOMOutput):
        print('can not find ' + MOMOutput)
        return
    
    DFO = dfo_summary
    #output
    #Final_Attributes_yyyymmddhhMOM+yyyymmddDFOUpdated.csv
    #Attributes_clean_yyyymmddhhMOM+yyyymmddDFOUpdated.csv 
    DFO_Final_Attributes_csv = 'Final_Attributes_{}HWRF+{}DFOUpdated.csv'.format(adate,dfo_date)
    DFO_Attributes_Clean_csv = 'Attributes_Clean_{}HWRF+{}DFOUpdated.csv'.format(adate,dfo_date)
    
    weightage = read_data('Weightage_DFO.csv')
    Attributes=read_data('Attributes.csv')
    PDC_resilience = read_data('Copy of Resilience_Index.csv')
    add_field_DFO=['DFO_area_1day_score', 'DFO_percarea_1day_score', 'DFO_area_2day_score', 'DFO_percarea_2day_score','DFO_area_3day_score', 'DFO_percarea_3day_score','DFOTotal_Score']

    #Read DFO Processing data and calculate score
    with open(DFO, 'r', encoding='UTF-8') as DFO_file:
        DFO_reader = csv.reader(DFO_file)
        DFO_w_score_csv = "DFO_w_score_{}.csv".format(dfo_date)
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
    Final_Output['Alert'] = Final_Output.apply(mofunc_dfo, axis=1)
    Final_Output.loc[Final_Output['Alert']=="Information",'Flag']=''
    Final_Output.loc[Final_Output['Alert']=="Advisory",'Flag']=''
    Final_Output.to_csv(DFO_Final_Attributes_csv, encoding='utf-8-sig')
    #Final_Output.to_csv('Final_Attributes_20210701_DFOUpdated.csv', encoding='utf-8-sig')
    join1 = pd.merge(Attributes, PDC_resilience[['ISO', 'Resilience_Index', ' NormalizedLackofResilience ']], on='ISO', how='inner')
    Attributes_Clean_DFO_Updated = pd.merge(join1.set_index('pfaf_id'), Final_Output[['Alert','Flag']], on='pfaf_id', how='right')
    Attributes_Clean_DFO_Updated.to_csv(DFO_Attributes_Clean_csv, encoding='utf-8-sig')
    os.remove(DFO_w_score_csv)

    # generate HWRF_DFO_VIIRS_MoM
    DFO_MOMOutput = DFO_Final_Attributes_csv
    VIIRS_summary_csv = viirs_summary

    #output files
    Final_Attributes_csv = "Final_Attributes_{}HWRF+{}DFO+{}VIIRSUpdated.csv".format(adate,dfo_date,viirs_date)
    Final_Attributes_csv = outputdir + Final_Attributes_csv
    Attributes_Clean_csv = "Attributes_clean_{}HWRF+{}DFO+{}VIIRSUpdated.csv".format(adate,dfo_date,viirs_date)
    Attributes_Clean_csv = outputdir + Attributes_Clean_csv
    
    weightage = read_data('VIIRS_Weightages.csv')
    Attributes=read_data('Attributes.csv')
    PDC_resilience = read_data('Copy of Resilience_Index.csv')
    add_field_VIIRS=['VIIRS_area_1day_score', 'VIIRS_percarea_1day_score', 'VIIRS_area_5day_score', 'VIIRS_percarea_5day_score','VIIRSTotal_Score']

    #Read VIIRS Processing data and calculate score
    with open(VIIRS_summary_csv, 'r', encoding='UTF-8') as VIIRS_file:
        VIIRS_reader = csv.reader(VIIRS_file)
        VIIRS_w_score_csv ="VIIRS_w_score_{}.csv".format(viirs_date)
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

    # remove DFO output
    os.remove(DFO_Final_Attributes_csv)
    os.remove(DFO_Attributes_Clean_csv)

    return

def final_alert_pdc(adate,hwrf6hourf,finalfolder):
    """ generate the output for the pdc final"""

    fAlert = 'Final_Attributes_{}HWRF+MOM+DFO+VIIRSUpdated_PDC.csv'.format(adate)
    if os.path.exists(finalfolder + fAlert):
        #print(fAlert)
        return
    # first find the hwrf hour output
    hwrfh_list = glob.glob(hwrf6hourf+"Final*.csv")
    #Final_Attributes_2021102800HWRF+20211028DFO+20211027VIIRSUpdated.csv
    matching = [s for s in hwrfh_list if adate+"HWRF" in s]
    if len(matching)<1:
        print("not found " + adate)
        return
    else:
        print(matching[0])
    aAlert = matching[0]
    # generate string from the previous day
    # turn the datestr into a real date
    datestr = adate[:-2]
    hh = adate[-2:]
    da = datetime.strptime(datestr,"%Y%m%d")
    pda = da - timedelta(days=1)
    pdatestr = pda.strftime("%Y%m%d")
    # pdate
    pdate = pdatestr + hh
    matching = [s for s in hwrfh_list if pdate+"HWRF" in s]
    # no previous date
    if len(matching)<1:
        # shall call the function to generate it
        print("not found " + pdate)
        return
    else:
        print(matching[0])
        
    pAlert=matching[0]

    mapping = {'Information': 1, 'Advisory': 2, 'Watch':3, 'Warning':4}
    PA=read_data(pAlert)
    CA=read_data(aAlert)
    CA['Status']=""
    PA=PA.replace({'Alert': mapping})
    CA=CA.replace({'Alert':mapping})

    pfaf_ID=set(CA['pfaf_id'].tolist())

    for i in pfaf_ID:
        #print(i)
        if i in PA.values:
            PAlert=PA.loc[PA['pfaf_id']==i,'Alert'].item()
        else:
            PAlert=5
        CAlert=CA.loc[CA['pfaf_id']==i,'Alert'].item()
        if PAlert ==5:
            CA.loc[CA['pfaf_id']==i,'Status']='New'
        elif PAlert==CAlert:
            CA.loc[CA['pfaf_id']==i,'Status']='Continued'
        elif (CAlert>PAlert):
            CA.loc[CA['pfaf_id']==i,'Status']='Upgraded'
        elif (CAlert<PAlert) & (PAlert!=5):
            CA.loc[CA['pfaf_id']==i,'Status']='Downgraded'
    
    mapping = {1:'Information', 2:'Advisory', 3:'Watch', 4:'Warning'}
    CA=CA.replace({'Alert':mapping})

    CA=CA.drop(['Admin0','Admin1','ISO','Resilience_Index',' NormalizedLackofResilience '],axis=1)
    Union_Attributes=pd.read_csv('Admin0_1_union_centroid.csv',encoding='Windows-1252')
    PDC_Alert= pd.merge(Union_Attributes, CA, on='pfaf_id', how='inner')
    #print(PDC_Alert)
    PDC_Alert.drop(PDC_Alert.index[(PDC_Alert['DFOTotal_Score']=='') & (PDC_Alert['MOM_Score']=='') & (PDC_Alert['CentroidY']>50)], inplace=True)
    PDC_Alert=PDC_Alert.drop(['FID_x', 'FID_y'],axis=1)
    PDC_Alert.to_csv(finalfolder+fAlert,encoding='Windows-1252')

    return


def main():
    # run batch mode

    testdate = "2021082612"
    home = os.path.expanduser("~")
    if os.path.exists(home + "/Projects"):
        home = home + "/Projects"
    gfmsf = home + "/ModelofModels/data/cron_data/gfms/"
    glofasf = home + "/ModelofModels/data/cron_data/glofas/"
    hwrff = home + "/ModelofModels/data/cron_data/HWRF/HWRF_summary/"
    outputf = home + "/ModelofModels/data/cron_data/HWRF/HWRF_MoM/"
    hwrfmomf = outputf
    dfof= home + "/ModelofModels/data/cron_data/DFO/DFO_summary/"
    viirsf = home + "/ModelofModels/data/cron_data/VIIRS/VIIRS_summary/"
    hwrf_hourf = home + "/ModelofModels/data/cron_data/HWRF/HWRF_DFO_VIIRS_MoM/"
    final_alertf = home + "/ModelofModels/data/cron_data/HWRF/HWRF_Final_Alert/"
    # debug
    #update_HWRFMoM_DFO_VIIRS(testdate,hwrfmomf,dfof,viirsf,hwrf_hourf)
    #return    
    
    for entry in sorted(os.listdir(hwrff))[-30:]:
        # extract adate
        #hwrf.2021080606rainfall.csv
        if ".csv" in entry:
            testdate = entry.split(".")[1].replace('rainfall',"")
            update_HWRF_MoM(testdate,gfmsf,glofasf,hwrff,outputf)
            update_HWRFMoM_DFO_VIIRS(testdate,hwrfmomf,dfof,viirsf,hwrf_hourf)
            final_alert_pdc(testdate,hwrf_hourf,final_alertf)

    rawf = home + "/ModelofModels/data/rawdata/hwrf/"
    for entry in sorted(os.listdir(rawf))[-30:]:
        #hwrf.2021092112rainfall.zip
        if ".zip" in entry:
            testdate = entry.split(".")[1].replace('rainfall',"")
            update_HWRF_MoM(testdate,gfmsf,glofasf,hwrff,outputf)
            update_HWRFMoM_DFO_VIIRS(testdate,hwrfmomf,dfof,viirsf,hwrf_hourf)
            final_alert_pdc(testdate,hwrf_hourf,final_alertf)

if __name__ == "__main__":
    main()
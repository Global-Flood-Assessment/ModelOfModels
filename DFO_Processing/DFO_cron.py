""" 
    DFO_cron.py
    -- cron script for DFO data
"""

import sys, os
import yaml
from datetime import date
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import subprocess

from DFO_process import DFO_process
from DFO_MoM import update_DFO_MoM

def load_config(onetime=''):
    """load configuration file """
    with open("DFO_config.yml", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    if onetime != "":
        if onetime == "key":
            entry = cfg['DFO']['key']
            return entry

    global hosturl
    hosturl = cfg['DFO']['host']
    current_year  = date.today().year
    hosturl += str(current_year)

    folderprefix = cfg['datalocation']['folderprefix']
    folderprefix = os.path.abspath(folderprefix) + os.path.sep
    global dfosummary
    dfosummary = folderprefix + cfg['datalocation']['dfosummary'] + os.path.sep
    global dfooutput
    dfooutput = folderprefix + cfg['datalocation']['dfooutput']
    global dforaw 
    dforaw = folderprefix + cfg['datalocation']['dforaw'] + os.path.sep
    global flood_dfo
    flood_dfo= folderprefix + cfg['datalocation']['flood_dfo'] + os.path.sep
    global flooddata
    flooddata= folderprefix + cfg['datalocation']['flooddata'] + os.path.sep

    """set up logging file"""
    logging.basicConfig(filename = cfg['datalocation']['loggingfile'], format='%(asctime)s %(message)s', level=logging.INFO)

def get_real_date(year,day_num):
    """ get the real date"""
    
    #allData/61/MCDWD_L3_NRT/2021/021

    #year,day_num = foldername.split("/")[-2:]
    res = datetime.strptime(year + "-" + day_num, "%Y-%j").strftime("%Y%m%d")

    return res

def check_status(adate):
    """ check if a give date is processed"""

    processed_list = os.listdir(dfosummary)
    processed = any(adate in x for x in processed_list)
    
    return processed

def generate_procesing_list():
    """ generate list of date to process"""
    reqs = requests.get(hosturl)
    soup = BeautifulSoup(reqs.text,"html.parser")
    
    cur_year = hosturl[-4:]

    datelist = {}
    for link in soup.find_all('a'):
        day_num = link.string
        if not day_num.isdigit():
            continue
        real_date = get_real_date(cur_year,day_num)
        if check_status(real_date):
            continue
        datelist[day_num]=real_date

    return datelist

def dfo_download(subfolder):
    """ download a subfolder """

    dfokey = load_config(onetime='key')
    dataurl = hosturl + "/" + subfolder
    wgetcmd = 'wget -r --no-parent -R .html,.tmp -nH -l1 --cut-dirs=8 {dataurl} --header "Authorization: Bearer {key}" -P {downloadfolder}'
    wgetcmd = wgetcmd.format(dataurl = dataurl,key=dfokey,downloadfolder=dforaw)
    #print(wgetcmd)
    subprocess.call(wgetcmd, shell=True)

    return


def DFO_cron():
    """ main code of DFO cron """
    basepath = os.path.dirname(os.path.abspath(__file__))

    load_config()
    print(hosturl)
    datelist = generate_procesing_list()
    if len(datelist) == 0:
        logging.info("no new data to process!")
        sys.exit(0)
    
    for key in datelist:
        logging.info("download: " + key)
        dfo_download(key)
        logging.info("download finished!")
        datafolder = dforaw  + key
        outputfolder = dfooutput
        logging.info("processing: " + key)
        DFO_process(datafolder,outputfolder,datestr=datelist[key])
        os.chdir(basepath)
        update_DFO_MoM(datelist[key],dfosummary,flooddata,flood_dfo)
        logging.info("processing finished!")
        os.chdir(basepath)
    
    #print(datelist)

def main():
    DFO_cron()

if __name__ == "__main__":
    main()
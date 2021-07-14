"""
    MoM_service_API.py
     
"""

import sys, os
from flask import Flask
from flask import request
from flask import Response
from flask import jsonify
from flask import send_from_directory

app = Flask(__name__)


"""test service is running"""
@app.route("/mom/test")
def test():
    info={}
    info["python"] = sys.version
    info["runningmode"] = app.debug
    return info["python"] + str(info["runningmode"])

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

@app.route("/mom/getdata")
def getdata():
    req_data = request.args.get('data').lower()
    req_date = request.args.get('date').lower()
    req_format = request.args.get('format').lower()

    availabledata = ['floodseverity']
    if not req_data in availabledata:
        not_found()
    
    adata = req_data
    adate = req_date
    aformat = req_format
    folderprefix = "../data/cron_data"
    basepath = os.path.abspath(folderprefix) + os.path.sep
    subfolder = {}
    subfolder["floodseverity_geojson"] = "gis_output"
    subfolder['floodseverity_csv'] = "flood_severity"
    
    #flood_warning_20200531.geojson
    if (adata == 'floodseverity') and (aformat=='geojson'):
        dataname = "flood_warning_" + adate + ".geosjon"
    
    #Attributes_Clean_20200516.csv	
    if (adata == 'floodseverity') and (aformat=='csv'):
        dataname = "Attributes_Clean_" + adate + ".csv"
    # check file exists
    datafile = basepath + subfolder[adata+"_"+aformat] + dataname 
    
    if not os.path.exists(datafile):
        not_found()
    
    try:
        return send_from_directory(basepath + subfolder[adata+"_"+aformat], filename=dataname, as_attachment=True)
    except FileNotFoundError:
        not_found()

if __name__ == "__main__":
    pass
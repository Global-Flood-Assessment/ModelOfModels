import sys
import os
from flask import Blueprint
from flask import jsonify
from flask import request
from flask import send_from_directory

from . dataservice import getGISdata

servedata = Blueprint(name="blueprint_x", import_name=__name__)

@servedata.route('/test', methods=['GET'])
def test():
    """
    ---
    get:
      description: test endpoint
      responses:
        '200':
          description: call successful
          content:
            application/json:
              schema: OutputSchema
      tags:
          - testing
    """
    output = {"msg": "I'm the test endpoint from servedata."}
    output['sys.version'] = sys.version
    return jsonify(output)

@servedata.errorhandler(404)
def not_found(error):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url + str(error),
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

@servedata.route('/data')
def getdata():
    """
        ---
        post:
        description: get GIS product for a given date
        requestBody:
            required: true
            content:
                application/json:
                    schema: InputSchema
        responses:
            '200':
            description: call successful
            content:
                application/json:
                schema: OutputSchema
        tags:
            - calculationdef getdata():
    """    
    # args
    # product = "HWRF" / "DFO" / "VIIRS"
    # format = geojson / kml
    # date = "YYYYMMDDHH" / "YYYYMMDD" / "latest"
    product_type = request.args['product']
    product_date = request.args['date']
    product_format = request.args['format']
    querys = {"product":product_type,"date":product_date,"format":product_format}

    gisdata = getGISdata(product_type,product_date,product_format)
    
    if "error" in gisdata:
        querys["error"] = gisdata
        return jsonify(querys)
    
    print(gisdata)
    try:
        return send_from_directory(os.path.dirname(gisdata), filename=os.path.basename(gisdata), as_attachment=True)
    except FileNotFoundError:
        not_found(gisdata)

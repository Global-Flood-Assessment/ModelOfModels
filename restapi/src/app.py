"""Flask Application"""

# load libaries
from flask import Flask, jsonify
import sys

# load modules
from src.endpoints.blueprint_servedata import servedata

# init Flask app
app = Flask(__name__)

# register blueprints. ensure that all paths are versioned!
app.register_blueprint(servedata, url_prefix="/api/v1/data")

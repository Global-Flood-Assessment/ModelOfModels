from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def index():
    glofas = "threspoints_2020050500"
    gfms = "Summary_Flood_byStor_2020051021"
    return render_template('index.html',glofas=glofas,gfms=gfms)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

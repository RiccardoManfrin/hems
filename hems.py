#!/usr/bin/python
from flask import Flask, render_template, jsonify
import random
import json
import DataMgr

production_W = 0
consumption_W = 0
app = Flask(__name__)
datamgr = DataMgr.DataMgr(period_check_s=5, store_interval_s=20, persist_interval_s=60)

@app.route('/')
def index():
	return render_template('./page.html')

@app.route('/graphs.js')
def graphs():
	return render_template('./graphs.js')

@app.route('/data/production/live')
def data_production_live():
	global datamgr
	return jsonify(datamgr.get_production_W())

@app.route('/data/consumption/live')
def data_consumption_live():
	global datamgr
	return jsonify(datamgr.get_consumption_W())

if __name__ == '__main__':

	app.run(host="0.0.0.0", port=3000, debug=True)
#!/usr/bin/python
from flask import Flask, render_template, jsonify
import random
import json
import DataMgr

production_W = 0
consumption_W = 0
app = Flask(__name__)
datamgr = DataMgr.DataMgr(period_sample_s=1)

@app.route('/')
def index():
	return render_template('./page.html')

@app.route('/graphs.js')
def graphs():
	return render_template('./graphs.js')

@app.route('/loading.js')
def loading():
	return render_template('./loading.js')

@app.route('/data/production/live')
def data_production_live():
	global datamgr
	return jsonify(datamgr.get_production_W())

@app.route('/data/consumption/live')
def data_consumption_live():
	global datamgr
	return jsonify(datamgr.get_consumption_W())

@app.route('/data/latest_live_data')
def latest_live_data():
	global datamgr
	return jsonify(datamgr.get_latest_live_data())

@app.route('/data/last_day')
def get_last_day_aggregate_data():
	global datamgr
	return jsonify(datamgr.get_last_day_aggregate_data())

@app.route('/data/daily')
def get_last_365_days_aggregate():
	global datamgr
	return jsonify(datamgr.get_last_365_days_aggregate())

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=3000, debug=False)
	
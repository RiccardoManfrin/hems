#!/usr/bin/python
from flask import Flask, render_template, jsonify
import random
import json

production_W = 0
consumption_W = 0
app = Flask(__name__)

@app.route('/')
def index():
	return render_template('./page.html')

@app.route('/graphs.js')
def graphs():
	return render_template('./graphs.js')

@app.route('/data/production/live')
def data_production_live():
	global production_W
	production_W = random.randint(-1,1) + production_W
	if production_W < 0:
		production_W = 0
	if production_W > 10:
		production_W = production_W / (production_W / 10) 
	return jsonify(production_W)

@app.route('/data/consumption/live')
def data_consumption_live():
	global consumption_W
	consumption_W = random.randint(-1,1) + consumption_W
	if consumption_W < 0:
		consumption_W = 0
	if consumption_W > 10:
		consumption_W = consumption_W / (consumption_W / 10) 
	return jsonify(consumption_W)

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=3000, debug=True)

import datetime
import time
import redis
import random
import schedule
import Adafruit_ADS1x15
from threading import Timer
from aurorapy.client import AuroraError, AuroraTCPClient, AuroraSerialClient

def now():
	return datetime.datetime.now()

def dtepoch_ms(dt):
	return int(time.mktime(dt.timetuple())) * 1000 + dt.microsecond / 1000

def today_elapsed_ms():
	today = datetime.date.today()
	today_datetime = datetime.datetime(
	    year=today.year, 
	    month=today.month,
	    day=today.day)
	return int((now() - today_datetime).total_seconds() * 1000)

def daily_ms():
	return 24*60*60*1000

def is_more_than_24h_ahead(epoch_ms):
	return ((dtepoch_ms(now()) - daily_ms()) > epoch_ms)   

class DataMgr:
	"""Data Manager"""
	def __init__(self, 
				period_sample_s=1, 			# How many times (consumption) data gets sampled  			
				aggregate_interval_s=3600):
		self.r = redis.StrictRedis(host='localhost', port=6379, db=0)
		self.lastaggregate= now()
		self.production_blink_ts = now()
		self.reset()
		self.period_check_s = 1
		self.aggregate_interval_s = aggregate_interval_s
		self.period_sample_s = period_sample_s
		self.adc = Adafruit_ADS1x15.ADS1115()
		self.inverter = AuroraSerialClient(port='/dev/ttyUSB0', address=2, 
			baudrate=19200, data_bits=8, parity='N', stop_bits=1, timeout=0.1, tries=3)
		try:
			self.inverter.connect()
		except AuroraError as e:
			self.log(str(e))
		Timer(self.period_check_s, self.check_to_aggregate_timeout, ()).start()
		Timer(self.period_sample_s, self.sample_cW_pW_Vgrid, ()).start()
		schedule.every().day.at("00:00").do(self.daily_aggregate)
		self.truncate_older_than_24h()

	def log(self, logstr):
		print str(now()) + "\t| " + logstr

	def sample_cW_pW_Vgrid(self):
		# Note you can change the I2C address from its default (0x48), and/or the I2C
		# bus by passing in these optional parameters:
		#adc = Adafruit_ADS1x15.ADS1015(address=0x49, busnum=1)

		# Choose a gain of 1 for reading voltages from 0 to 4.09V.
		# Or pick a different gain to change the range of voltages that are read:
		#  - 2/3 = +/-6.144V
		#  -   1 = +/-4.096V
		#  -   2 = +/-2.048V
		#  -   4 = +/-1.024V
		#  -   8 = +/-0.512V
		#  -  16 = +/-0.256V
		# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
		GAIN = 1
		V = max(0, self.adc.read_adc(0, gain=GAIN) * 124.77 / 1000000.0)
		c_W = int(V / 0.12 * 580)
		p_W = 0
		V_grid = 0
		try:
			p_W = int(self.inverter.measure(3, global_measure=True))
			V_grid = int(self.inverter.measure(1, global_measure=True))
		except AuroraError as e:
			pass
		self.set(p_W, c_W, V_grid)
		Timer(self.period_sample_s, self.sample_cW_pW_Vgrid, ()).start()

	def production_blink(self):
		# Just register this API on rising edge and you're done following here
		##http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3
		p_W = 3600 / (now() - self.production_blink_ts).total_seconds()
		self.production_blink_ts = now()
		self.set(p_W=p_W)

	def check_to_aggregate_timeout(self):
		_now = now()
		if (_now - self.lastaggregate).seconds > self.aggregate_interval_s:
			self.lastaggregate = _now
			self.aggregate_store()
		schedule.run_pending()
		Timer(self.period_check_s, self.check_to_aggregate_timeout, ()).start()
	
	def aggregate_store(self):
		self.log("Data aggregation routine")
		self.r.rpush('aggregate_ts_ms_since_epoch', dtepoch_ms(self.lastupdate))
		self.r.rpush('p_Wh', self.p_Wh)
		self.r.rpush('c_Wh', self.c_Wh)
		self.r.rpush('a_Wh', self.a_Wh)
		self.r.rpush('s_Wh', self.s_Wh)
		self.r.rpush('b_Wh', self.b_Wh)
		self.reset_aggregate()
		self.truncate_older_than_24h()

	def daily_aggregate(self):
		self.log("Aggregating daily data")
		aggregate_len = self.r.llen('aggregate_ts_ms_since_epoch')
		daily_p_Wh = 0
		daily_c_Wh = 0
		daily_a_Wh = 0
		daily_s_Wh = 0
		daily_b_Wh = 0
		for i in range(0, aggregate_len):
			daily_p_Wh = daily_p_Wh+ float(self.r.lindex('p_Wh', i))
			daily_c_Wh = daily_c_Wh+ float(self.r.lindex('c_Wh', i))
			daily_a_Wh = daily_a_Wh+ float(self.r.lindex('a_Wh', i))
			daily_s_Wh = daily_s_Wh+ float(self.r.lindex('s_Wh', i))
			daily_b_Wh = daily_b_Wh+ float(self.r.lindex('b_Wh', i))

		self.r.rpush('daily_epoch_ms', dtepoch_ms(now()))
		self.r.rpush('daily_p_Wh', daily_p_Wh)
		self.r.rpush('daily_c_Wh', daily_c_Wh)
		self.r.rpush('daily_a_Wh', daily_a_Wh)
		self.r.rpush('daily_s_Wh', daily_s_Wh)
		self.r.rpush('daily_b_Wh', daily_b_Wh)
		self.truncate_older_than_24h()

	def truncate_older_than_24h(self):
		a_ts = self.r.lindex('aggregate_ts_ms_since_epoch', 0)
		if not a_ts:
			return
		epoch_ms = float(a_ts)
		while is_more_than_24h_ahead(epoch_ms):
			self.r.lpop('aggregate_ts_ms_since_epoch')
			self.r.lpop('p_Wh')
			self.r.lpop('c_Wh')
			self.r.lpop('a_Wh')
			self.r.lpop('s_Wh')
			self.r.lpop('b_Wh')
			epoch_ms = float(self.r.lindex('aggregate_ts_ms_since_epoch', 0))


	def live_store(self):
		self.r.rpush('ts_ms_since_epoch', dtepoch_ms(self.lastupdate))
		self.r.rpush('p_W', self.now_p_W)
		self.r.rpush('c_W', self.now_c_W)
		self.r.rpush('V_grid', self.now_V_grid)

		while self.r.llen('ts_ms_since_epoch') > 300:
			self.r.lpop('ts_ms_since_epoch')
		while self.r.llen('p_W') > 300:
			self.r.lpop('p_W')
		while self.r.llen('c_W') > 300:
			self.r.lpop('c_W')
		while self.r.llen('V_grid') > 300:
			self.r.lpop('V_grid')
 
	def get_latest_live_data(self):
		res = { 
				'ts_ms_since_epoch' : map(int, self.r.lrange('ts_ms_since_epoch', 0, -1)) ,
				'p_W' : map(float, self.r.lrange('p_W', 0, -1)) ,
				'c_W' : map(float, self.r.lrange('c_W', 0, -1)) ,
				'V_grid' : map(float, self.r.lrange('V_grid', 0, -1)) ,
				}
		return res

	def get_last_day_aggregate_data(self):
		res = {
			'aggregate_ts_ms_since_epoch' : map(int, self.r.lrange('aggregate_ts_ms_since_epoch', 0, -1)),
			'p_Wh' : map(float, self.r.lrange('p_Wh', 0, -1)),
			'c_Wh' : map(float, self.r.lrange('c_Wh', 0, -1)),
			'a_Wh' : map(float, self.r.lrange('a_Wh', 0, -1)),
			's_Wh' : map(float, self.r.lrange('s_Wh', 0, -1)),
			'b_Wh' : map(float, self.r.lrange('b_Wh', 0, -1))
		}

		return res

	def get_last_365_days_aggregate(self):
		res = {
			'daily_epoch_ms' :map(int, self.r.lrange('daily_epoch_ms', -365, -1)),
			'daily_p_Wh' :map(float, self.r.lrange('daily_p_Wh', -365, -1)),
			'daily_c_Wh' :map(float, self.r.lrange('daily_c_Wh', -365, -1)),
			'daily_a_Wh' :map(float, self.r.lrange('daily_a_Wh', -365, -1)),
			'daily_s_Wh' :map(float, self.r.lrange('daily_s_Wh', -365, -1)),
			'daily_b_Wh' :map(float, self.r.lrange('daily_b_Wh', -365, -1))
		}
		return res

	def get_production_W(self):
		return self.now_p_W

	def get_consumption_W(self):
		return self.now_c_W

	def get_V_grid(self):
		return self.now_V_grid

	def get_day_production_Wh(self):
		return self.p_Wh

	def get_day_consumption_Wh(self):
		return self.c_Wh

	def get_day_auto_consumed_Wh(self):
		return self.a_Wh

	def get_day_bought_Wh(self):
		return self.b_Wh

	def set(self, p_W=-1, c_W=-1, V_grid=-1):

		if p_W == -1:
			p_W = self.now_p_W

		if c_W == -1:
			c_W = self.now_c_W

		if V_grid == -1:
			V_grid = self.now_V_grid

		elapsed = ((now() - self.lastupdate).total_seconds())
		a_W = min(p_W, c_W) #autoconsumed
		s_W = (p_W - a_W)   #sold
		b_W = (c_W - a_W)   #bought
		self.p_Wh = self.p_Wh + (p_W * elapsed / 3600) #produced [Wh]
		self.c_Wh = self.c_Wh + (c_W * elapsed / 3600) #consumed [Wh]
		self.a_Wh = self.a_Wh + (a_W * elapsed / 3600) #auto-consumed [Wh]
		self.s_Wh = self.s_Wh + (s_W * elapsed / 3600) #sold [Wh]
		self.b_Wh = self.b_Wh + (b_W * elapsed / 3600) #bought [Wh]
		self.now_p_W = p_W
		self.now_c_W = c_W
		self.now_V_grid = V_grid
		self.lastupdate = now() 
		self.live_store()

	def reset(self):
		self.now_p_W = 0
		self.now_c_W = 0
		self.lastupdate = now()
		self.reset_aggregate()

	def reset_aggregate(self):
		self.p_Wh = 0 #produced [Wh]
		self.c_Wh = 0 #consumed [Wh]
		self.a_Wh = 0 #auto-consumed [Wh]
		self.s_Wh = 0 #sold [Wh]
		self.b_Wh = 0 #bought [Wh]

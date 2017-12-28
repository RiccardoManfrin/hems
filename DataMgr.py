
import datetime
import time
import redis
import random
import schedule
from threading import Timer

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
	return ((dtepoch_ms(now()) - daily_ms) > epoch_ms)   

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
		Timer(self.period_check_s, self.timeout, ()).start()
		Timer(self.period_sample_s, self.sample_consumption, ()).start()
		schedule.every().day.at("00:00").do(self.daily_aggregate)
	
	def log(self, logstr):
		print str(now()) + "\t| " + logstr

	def sample_consumption(self):
		newconsump = (self.now_c_W + random.randint(500,2000)) / 2
		self.set(c_W=newconsump)
		Timer(self.period_sample_s, self.sample_consumption, ()).start()

	def production_blink(self):
		# Just register this API on rising edge and you're done following here
		##http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3
		p_W = 3600 / (now() - self.production_blink_ts).total_seconds()
		self.production_blink_ts = now()
		self.set(p_W=p_W)

	def timeout(self):
		_now = now()
		if (_now - self.lastaggregate).seconds > self.aggregate_interval_s:
			self.lastaggregate = _now
			self.aggregate_store()
		Timer(self.period_check_s, self.timeout, ()).start()
	
	def aggregate_store(self):
		self.log("Data aggregation routine")
		self.r.rpush('aggregate_ts_ms_since_epoch', dtepoch_ms(self.lastupdate))
		self.r.rpush('p_Wh', self.p_Wh)
		self.r.rpush('c_Wh', self.c_Wh)
		self.r.rpush('a_Wh', self.a_Wh)
		self.r.rpush('s_Wh', self.s_Wh)
		self.r.rpush('b_Wh', self.b_Wh)
		self.reset_aggregate()

	def daily_aggregate(self):
		print "Aggregating daily data"
		aggregate_len = self.r.llen('aggregate_ts_ms_since_epoch')
		daily_p_Wh = 0
		daily_c_Wh = 0
		daily_a_Wh = 0
		daily_s_Wh = 0
		daily_b_Wh = 0
		for i in range(0, aggregate_len):
			daily_p_Wh = daily_p_Wh+ self.r.lrange('p_Wh', i, i)
			daily_c_Wh = daily_c_Wh+ self.r.lrange('c_Wh', i, i)
			daily_a_Wh = daily_a_Wh+ self.r.lrange('a_Wh', i, i)
			daily_s_Wh = daily_s_Wh+ self.r.lrange('s_Wh', i, i)
			daily_b_Wh = daily_b_Wh+ self.r.lrange('b_Wh', i, i)

		self.r.rpush('daily_epoch_ms', dtepoch_ms(now()))
		self.r.rpush('daily_p_Wh', daily_p_Wh)
		self.r.rpush('daily_c_Wh', daily_c_Wh)
		self.r.rpush('daily_a_Wh', daily_a_Wh)
		self.r.rpush('daily_s_Wh', daily_s_Wh)
		self.r.rpush('daily_b_Wh', daily_b_Wh)

		epoch_ms = self.r.lrange('aggregate_ts_ms_since_epoch', 0, 0)
		while is_more_than_24h_ahead(epoch_ms):
			self.r.lpop('aggregate_ts_ms_since_epoch')
			self.r.lpop('daily_p_Wh')
			self.r.lpop('daily_c_Wh')
			self.r.lpop('daily_a_Wh')
			self.r.lpop('daily_s_Wh')
			self.r.lpop('daily_b_Wh')


	def live_store(self):
		self.r.rpush('ts_ms_since_epoch', dtepoch_ms(self.lastupdate))
		self.r.rpush('p_W', self.now_p_W)
		self.r.rpush('c_W', self.now_c_W)
		while self.r.llen('ts_ms_since_epoch') > 300:
			self.r.lpop('ts_ms_since_epoch')
		while self.r.llen('p_W') > 300:
			self.r.lpop('p_W')
		while self.r.llen('c_W') > 300:
			self.r.lpop('c_W')
 
	def get_latest_live_data(self):
		res = { 
				'ts_ms_since_epoch' : map(int, self.r.lrange('ts_ms_since_epoch', 0, -1)) ,
				'p_W' : map(float, self.r.lrange('p_W', 0, -1)) ,
				'c_W' : map(float, self.r.lrange('c_W', 0, -1)) ,
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

	def get_day_production_Wh(self):
		return self.p_Wh

	def get_day_consumption_Wh(self):
		return self.c_Wh

	def get_day_auto_consumed_Wh(self):
		return self.a_Wh

	def get_day_bought_Wh(self):
		return self.b_Wh

	def set(self, p_W=-1, c_W=-1):

		if p_W == -1:
			p_W = self.now_p_W

		if c_W == -1:
			c_W = self.now_c_W

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

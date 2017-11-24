
import datetime
import time
import redis
import random
from threading import Timer

def now():
	return datetime.datetime.now()

def dtepoch(dt):
	return int(time.mktime(dt.timetuple()))

class DataMgr:
	"""Data Manager"""
	def __init__(self, 
				period_sample_s=1, 
				period_check_s=10, 
				store_interval_s=3600, 
				persist_interval_s=3600*24):
		self.r = redis.StrictRedis(host='localhost', port=6379, db=0)
		self.lastaggregate= now()
		self.production_blink_ts = now()
		self.reset()
		self.period_check_s = period_check_s
		self.store_interval_s = store_interval_s
		self.persist_interval_s = persist_interval_s
		self.period_sample_s = period_sample_s
		Timer(self.period_check_s, self.timeout, ()).start()
		Timer(self.period_sample_s, self.sample_consumption, ()).start()
	
	def sample_consumption(self):
		self.set(c_W=random.randint(500,2000))
		Timer(self.period_sample_s, self.sample_consumption, ()).start()

	def production_blink(self):
		# Just register this API on rising edge and you're done following here
		##http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3
		p_W = 3600 / (now() - self.production_blink_ts).total_seconds()
		self.production_blink_ts = now()
		self.set(p_W=p_W)

	def timeout(self):
		_now = now()
		if (_now - self.lastaggregate).seconds > self.store_interval_s:
			self.lastaggregate = _now
			self.aggregate_store()
		Timer(self.period_check_s, self.timeout, ()).start()
	
	def aggregate_store(self):
		print "Data aggregation routine"
		self.r.rpush('aggregate_ts_ms_since_epoch', dtepoch(self.lastupdate))
		self.r.rpush('p_Wh', self.p_Wh)
		self.r.rpush('c_Wh', self.c_Wh)
		self.r.rpush('a_Wh', self.a_Wh)
		self.r.rpush('s_Wh', self.s_Wh)
		self.r.rpush('b_Wh', self.b_Wh)
		#TODO
		self.aggregate_reset()

	def live_store(self):
		self.r.rpush('ts_ms_since_epoch', dtepoch(self.lastupdate))
		self.r.rpush('p_W', self.now_p_W)
		self.r.rpush('c_W', self.now_c_W)
		while self.r.llen('ts_ms_since_epoch') > 300:
			self.r.lpop('ts_ms_since_epoch')
		while self.r.llen('p_W') > 300:
			self.r.lpop('p_W')
		while self.r.llen('c_W') > 300:
			self.r.lpop('c_W')
 
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

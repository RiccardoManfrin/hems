
import datetime
from threading import Timer
def now():
	return datetime.datetime.now()

class DataMgr:
	def __init__(self):
		self.now_p_W = 0
		self.now_c_W = 0
		self.lastupdate = now() 
		self.daily_p_Wh = 0 #produced
		self.daily_c_Wh = 0 #consumed
		self.daily_a_Wh = 0 #auto-consumed
		self.daily_s_Wh = 0 #sold
		self.daily_b_Wh = 0 #bought
		Timer(10, self.timeout, ()).start()
	
	def timeout(self):
		print "timeoutmanaged"
		Timer(10, self.timeout, ()).start()
	
	def get_production_W(self):
		return self.now_p_W

	def get_consumption_W(self):
		return self.now_c_W

	def get_day_production_Wh(self):
		return self.daily_p_Wh

	def get_day_consumption_Wh(self):
		return self.daily_c_Wh

	def get_day_auto_consumed_Wh(self):
		return self.daily_a_Wh

	def get_day_bought_Wh(self):
		return self.daily_b_Wh

	def set(self, p_W, c_W):
		elapsed = ((now() - self.lastupdate).total_seconds())
		a_W = min(p_W, c_W)
		s_W = (p_W - a_W)
		b_W = (c_W - a_W)
		self.daily_p_Wh = self.daily_p_Wh + (p_W * elapsed / 3600) #produced
		self.daily_c_Wh = self.daily_c_Wh + (c_W * elapsed / 3600) #consumed
		self.daily_a_Wh = self.daily_a_Wh + (a_W * elapsed / 3600) #auto-consumed
		self.daily_s_Wh = self.daily_s_Wh + (s_W * elapsed / 3600) #sold
		self.daily_b_Wh = self.daily_b_Wh + (b_W * elapsed / 3600) #bought

		self.now_p_W = p_W
		self.now_c_W = c_W
		self.lastupdate = now() 

	def reset(self):
		self.now_p_W = 0
		self.now_c_W = 0
		self.lastupdate = now() 
		self.daily_p_Wh = 0 #produced
		self.daily_c_Wh = 0 #consumed
		self.daily_a_Wh = 0 #auto-consumed
		self.daily_s_Wh = 0 #sold
		self.daily_b_Wh = 0 #bought


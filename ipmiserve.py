
#
# Parse command line arguments
#
import argparse
parser = argparse.ArgumentParser(description='IPMI Monitoring Tool.')
parser.add_argument('--ip', 		dest='ip', required=True, help='The IP address of the IPMI interface')
parser.add_argument('--port', 		dest='port', type=int, default=623, help='The port of the IPMI interface')
parser.add_argument('--username', 	dest='username', default="admin", help='The authentication username for the IPMI interface')
parser.add_argument('--password', 	dest='password', default="admin", help='The authentication password for the IPMI interface')
parser.add_argument('--records',	dest='records', required=True, metavar='RECORD_ID', type=int, nargs='+', help='The sensor(s) to retrieve via the record id')
args = parser.parse_args()
print(args)

#
# Connect to the IPMI interface
#
from ipmimon import IpmiMon
mon = IpmiMon(	logfile		= "/tmp/ipmimon.txt", 
                ip			= args.ip, 
                username	= args.username,
				password	= args.password,
                records		= args.records )
mon.run()

import sys
sys.exit(0)

import tornado.web
from tornado.ioloop import IOLoop
from tornado import gen
import time

class TestHandler(tornado.web.RequestHandler):
	@gen.coroutine
	def get(self):
		print("test")
		self.write("ok")

class PingHandler(tornado.web.RequestHandler):
	@gen.coroutine
	def get(self):
		print("ping")

class MarkHandler(tornado.web.RequestHandler):
	@gen.coroutine
	def get(self):
		for arg in self.request.arguments:
			parm = self.get_argument(arg,None)
			print(arg,parm)

app = tornado.web.Application(
	[ 	(r"/test", TestHandler), 
		(r"/ping", PingHandler),	
		(r"/mark", MarkHandler)	
	] )

app.listen(3000)
IOLoop.instance().start()

print("done")


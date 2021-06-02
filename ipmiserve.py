
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
parser.add_argument('--listen', 	dest='listen', type=int, required=True, help='The listen port for HTTP commands')
args = parser.parse_args()

#
# Create a file logger
#
import datetime
path = "/tmp/%s" % datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
from ipmilogger import IpmiLogger
logger = IpmiLogger(path)
print("Created a logger at '%s'" % path)

#
# Connect to the IPMI interface
#
from ipmimon import IpmiMon
mon = IpmiMon(	ip			= args.ip, 
                username	= args.username,
				password	= args.password,
                records		= args.records,
				logger		= logger )
print("Connected to the IPMI interface at %s" % args.ip)

# TODO: sample one
# mon.run()

#
# Listen and respond to http messages
#
import tornado.web
from tornado.ioloop import IOLoop
from tornado import gen
import time

class LogHandler(tornado.web.RequestHandler):

	def initialize(self, logger):
		self.logger = logger
		
	@gen.coroutine
	def get(self):
		for arg in self.request.arguments:
			parm = self.get_argument(arg,None)
			self.logger.log( "%s = %s" % (arg,parm), echo=True)
		self.write("ok")

app = tornado.web.Application(
	[ 		
		(r"/log", LogHandler, {'logger':logger} )
	])
app.logger = logger

app.listen(args.listen)
print("Listing on port %d" % args.listen)
IOLoop.instance().start()


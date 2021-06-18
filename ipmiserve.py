
def main():
        #
        # Parse command line arguments
        #
        import  sys
        import  argparse
        parser  = argparse.ArgumentParser(description='IPMI Monitoring Tool.')
        parser.add_argument('--ip',         dest='ip', required=True, help='The IP address of the IPMI interface')
        parser.add_argument('--port',       dest='port', type=int, default=623, help='The port of the IPMI interface')
        parser.add_argument('--username',   dest='username', default="admin", help='The authentication username for the IPMI interface')
        parser.add_argument('--password',   dest='password', default="admin", help='The authentication password for the IPMI interface')
        parser.add_argument('--enumerate',  dest='enumerate', default=False, action="store_true", help='Enumerate all available sensors showing sensor name and record id')
        parser.add_argument('--records',    dest='records', required=False, default=None, metavar='RECORD_ID', type=int, nargs='+', help='The sensor(s) to retrieve via the record id')
        parser.add_argument('--listen',     dest='listen', type=int, default=None, required=False, help='The listen port for HTTP commands')
        parser.add_argument('--delay',      dest='delay', type=int, default=1, help='The delay/sleep time between queries to the IPMI interface for a set of sensors')
        parser.add_argument('--path',       dest='path', default="/tmp/impi", help='Supply a directory where timestamped log files will be written.')
        parser.add_argument('--sessions',   dest='sessions', action='store_true', help='Will return power consumption via web requests.')

        args    = parser.parse_args()

        if not args.enumerate and not args.records:
            print("--enumerate or --records argument needs to be supplied.")
            parser.print_help()
            parser.exit()
            sys.exit(1)
    
        #
        # Create the output directory as needed
        #
        import os
        if not os.path.exists( args.path ):
            print("Warning: Making directory %s" % args.path)
            os.makedirs(args.path, exist_ok=True)   
    
        #
        # Create a file logger
        #
        import  datetime
        path    = os.path.join( args.path, "%s" % datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S") )
        from    ipmilogger import IpmiLogger
        logger  = IpmiLogger(path,sessions=args.sessions)
        print("Created a logger at '%s'" % path)

        #
        # Connect to the IPMI interface
        #
        from    ipmimon import IpmiMon
        mon     = IpmiMon(  ip          = args.ip, 
                            username    = args.username,
                            password    = args.password,
                            records     = args.records,
                            logger      = logger,
                            delay       = args.delay)
        print("Connecting to the IPMI interface at %s..." % args.ip)
        mon.connect()
        print("Connected to the IPMI interface at %s." % args.ip)

        #
        # Enumerate sensors if requested
        #
        if  args.enumerate:
            mon.enumerate_sensors()
            sys.exit(0)

        #
        # Monitor sensors ( don't listen for http commands )
        #
        if  not args.listen:
            print("Monitoring the following records: ", args.records )
            mon.run()

        #
        # Listen and respond to http messages
        #
        import  tornado.web
        from    tornado.ioloop import IOLoop
        from    tornado import gen
        from    tornado import concurrent
        import  urllib.parse
        import  json

        executor = concurrent.futures.ThreadPoolExecutor(8)
        def task(mon):
            mon.run()
        executor.submit(task, mon)

        class LogHandler(tornado.web.RequestHandler):

            def initialize(self, logger):
                self.logger = logger
                
            @gen.coroutine
            def get(self):
                try:
                    log_item = ""
                    for arg in self.request.arguments:
                        if log_item: log_item += ","
                        parm = self.get_argument(arg,None)
                        if arg.endswith("_enc"): parm = parm = urllib.parse.unquote(parm)
                        log_item += "%s = %s" % (arg,parm)
                    ret_val = self.logger.log( log_item, echo=True)
                    if ret_val:
                        self.write(json.dumps(ret_val))
                    else:
                        self.write(json.dumps("its ok"))
                except:
                    print("ERR:", sys.exc_info()[0], sys.exc_info()[1])

        app = tornado.web.Application(
            [       
                (r"/log", LogHandler, {'logger':logger} )
            ])
        app.logger = logger

        app.listen(args.listen)
        print("Listing on port %d" % args.listen)
        IOLoop.instance().start()


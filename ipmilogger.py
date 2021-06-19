import os
import datetime
import tempfile
import sys
from scipy.integrate import simps
from numpy import trapz
import pandas as pd
import traceback

class IpmiLogger:
    """This class abstracts to logging-to-file functions needed by the 
    ipmicap package.
    """

    def __init__(self,  path=None, overwrite=False, echo=False, sessions=False ):
        
        if path!=None and  not overwrite and os.path.exists(path):
            raise Exception("The file '%s' exists." % path)

        f = open(path,'w')
        f.write("IpmiLogger: %s\n" % path )
        f.flush()
        f.close()

        self.path = path
        self.echo = echo
        self.sessions = sessions
        self.cur_cap_session    = None
        self.capture_sessions   = {}
        self.session_started    = False
        self.started            = None
        self.sensors            = {}

    def log(self, message, echo=None):
        """"
        This function logs a messages to the log file.
        """

        f = open(self.path,'a')
        now = datetime.datetime.now()
        line = now.strftime("%Y-%m-%d_%H:%M:%S") + " -- " + message
        f.write( line  + "\n" )
        f.flush()
        f.close()

        if self.echo:
            if echo==None or echo==True: print(line)
            else: pass
        else:
            if echo==True: print(line)
            else: pass
        
        return now

#
# To run the unit tests below for IpmiLogger, type "python ipmilogger.py"
#
if __name__ == "__main__":

    path = tempfile.mkstemp()[1]
    print("Created temp file %s\n" % path)

    logger = IpmiLogger( path=path, overwrite=True, echo=True )
    logger.log("test")

    f = open(path)
    contents = f.read()
    f.close()
    print("\nlog file contents->\n%s" % contents)

    os.unlink(path)

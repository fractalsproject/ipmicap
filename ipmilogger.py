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

        if self.sessions:
            return self._process_session(now, message)
        else:
            return 
        

    def _process_session(self, dt, message):

        # TODO: Should redo this state machine to something cleaner
        try:
            pieces = message.split(",")
            for piece in pieces:
          
                if piece.startswith("ping"):
                    pass
                elif piece.startswith("SENSOR:"):
                    pass
                elif piece.startswith("start"):
                    self.started = dt
                elif piece.startswith("id"):
                    parts = piece.split("=")
                    self.cur_cap_session = parts[1].strip()
                    self.capture_sessions[self.cur_cap_session] = []
                elif piece.startswith("stop"):
                    if not self.started:
                        print("Warning: No session was started for the stop cmd.")
                    else:
                        power_cons = self._compute_session( self.started, dt, self.cur_cap_session )
                        self.started = False
                        self.cur_cap_session = None
                        return power_cons
                else: # we assume its a sensor 
                    parts = piece.split(":")
                    sensor_id = int(parts[0].strip())
                    val = float(parts[1].strip())
                    self.sensors[sensor_id] = True
                    if self.started:
                        self.capture_sessions[self.cur_cap_session].append( [dt, sensor_id, val] )
                    else:
                        pass
        except:
            print("ERR:", sys.exc_info()[0], sys.exc_info()[1] )
                
    def _compute_session(self, start_time, end_time, session_id):
 
        ready_for_df = [] 
        for item in self.capture_sessions[session_id]:
            ready_for_df.append( item )

        df = pd.DataFrame(ready_for_df, columns =['dt','sensor_id','value'])

        per_sensor = {}
        for sensor_id in self.sensors.keys():
            per_sensor[sensor_id] = []
            new_df = df.loc[ df['sensor_id'] == sensor_id  ]
            dt_val = new_df[['dt','value']].values.tolist()
            dt, val = zip(*dt_val)
            # prepend the start and end endpoints and (TODO) interpolate their values
            dt = [start_time] + list(dt) + [end_time]
            val = [ val[0] ] + list(val) + [ val[-1] ]
            cdt = [ (t-dt[0]).total_seconds() for t in dt ]
            per_sensor[sensor_id] = [cdt, val]

        powers = {}
        for idx,sensor_id in enumerate(self.sensors.keys()):
            cdt = per_sensor[sensor_id][0]
            val = per_sensor[sensor_id][1]
            tarea = trapz(val,cdt)
            sarea = simps(val,cdt)
            powers[sensor_id] = tarea
        
        tot_power = 0
        for sensor_id in self.sensors.keys():
            tot_power += powers[sensor_id]

        return tot_power 
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

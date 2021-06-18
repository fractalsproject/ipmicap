import os
import datetime
import tempfile
import sys
from scipy.integrate import simps
from numpy import trapz
import pandas as pd

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

        try:
            parts = message.split()
            cmd = parts[0].strip()

            #print("cmd=",cmd)
            if cmd == "ping":
                pass
            elif cmd.startswith("SENSOR:"):
                pass
            elif cmd  == "start":
                self.started = dt
            elif cmd == "id":
                self.cur_cap_session = parts[2].strip()
                self.capture_sessions[self.cur_cap_session] = []
            elif cmd == "stop":
                if not self.started:
                    print("Warning: No session was started for the stop cmd.")
                else:
                    power_cons = self._compute_session( self.started, dt, self.cur_cap_session )
                    self.started = False
                    self.cur_cap_session = None
                    print("Returning power", power_cons)
                    return power_cons
            else: # we assume its a sensor 
                sensor_id = int(parts[0].strip())
                val = float(parts[2].strip())
                self.sensors[sensor_id] = True
                #print(sensor_id, val)
                if self.started:
                    self.capture_sessions[self.cur_cap_session].append( [dt, sensor_id, val] )
                else:
                    pass
        except:
            print("ERR: Processing session.", sys.exc_info()[0], sys.exc_info()[1])
                
    def _compute_session(self, start_time, end_time, session_id):
        print("len sessions=", len(self.capture_sessions) )
        print("captures=", self.capture_sessions[session_id])
   
        ready_for_df = [] 
        #for key in prev.keys():
        #    ready_for_df.append( prev[key] )

        for item in self.capture_sessions[session_id]:
            ready_for_df.append( item )

        df = pd.DataFrame(ready_for_df, columns =['dt','sensor_id','value'])
        print(df.to_string())

        per_sensor = {}
        for sensor_id in self.sensors.keys():
            per_sensor[sensor_id] = []
            new_df = df.loc[ df['sensor_id'] == sensor_id  ]
            dt_val = new_df[['dt','value']].values.tolist()
            dt, val = zip(*dt_val)
            # prepend the start and end endpoints and (TODO) interpolate their values
            print("pre",dt,val, start_time, end_time)
            dt = [start_time] + list(dt) + [end_time]
            print("dt=",dt)
            val = [ val[0] ] + list(val) + [ val[-1] ]
            print("val=",val)
            cdt = [ (t-dt[0]).total_seconds() for t in dt ]
            per_sensor[sensor_id] = [cdt, val]
        print(per_sensor)

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

import os
import datetime
import tempfile
import sys
from scipy.integrate import simps
from numpy import trapz
import pandas as pd

class IpmiSessionManager:
    """This class provides capture sessions and computatations on the 
    collected session sensor data.
    """

    def __init__(self, debug=False):

        self.session_started    = False
        self.started            = {}
        self.sensors            = {}
        self.capture_sessions   = {}
        self.debug              = debug

    def start(self, dt, session_id):

        self.started[session_id]  = dt
        self.capture_sessions[session_id] = []

    def stop(self, dt, session_id, all_stats=False):
        if not session_id in self.capture_sessions:
            print("ERR: invalid session_id for stop", session_id )
            return -1

        if not self.started[session_id]:
            print("Warning: No session was started for", session_id) 
            return -1
        else:
            power_stats = self._compute_session( self.started[session_id], dt, session_id )
            self.started.pop(session_id, None)
            self.capture_sessions.pop(session_id, None)
            if all_stats:
                return power_stats
            else:
                return power_stats["tot_power"]

    def sensor(self, dt, sensor_id, value):

        self.sensors[sensor_id] = True
        for session_id in self.capture_sessions.keys():
            if self.started[session_id]:
                self.capture_sessions[session_id].append( [dt, sensor_id, value] )
        else:
            pass

    def nvidia_sensor(self, dt, nv_id, value):

        sname = "nvidia-%d" % nv_id
        self.sensors[sname] = True
        for session_id in self.capture_sessions.keys():
            if self.started[session_id]:
                self.capture_sessions[session_id].append( [dt, sname, value] )
        else:
            pass

    def g2_sensor(self, dt, g2, value):

        sname = "apu-%02d" % g2
        self.sensors[sname] = True
        for session_id in self.capture_sessions.keys():
            if self.started[session_id]:
                self.capture_sessions[session_id].append( [dt, sname, value] )
        else:
            pass

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
            if len(dt_val)==0: 
                print("ERR: No sensor samples found")
                return -1
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
            if type(sensor_id)==type("") and sensor_id.startswith("nvidia"):
                print("Warning: Skipping nvidia sensor in session total power compute")
                continue
            if type(sensor_id)==type("") and sensor_id.startswith("apu"):
                print("Warning: Skipping apu sensor in session total power compute")
                continue
            tot_power += powers[sensor_id]

        return {"per_sensor":per_sensor, "tot_power":tot_power, "powers":powers, "start_time":str(start_time), "end_time":str(end_time)}


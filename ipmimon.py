import pyipmi
import pyipmi.interfaces
import time
import os
import sys
import traceback
import datetime
import re

#
# configuration
#
#Power (V)       : 27.429188
GSI_TOOL_POWER_REGEX = re.compile(".*Power\s*\(V\)\s+\:\s+(.*)", re.MULTILINE)
GSI_TOOL_POWER_REGEX = "Power\s*\(V\)\s+\:\s+(.*)"

class IpmiMon:
    """
    This class abstracts the communication with the IPMI interface for a chassis system.
    It provides these functions:
        * enumerates the available sensors
        * samples requests sensors with a time delay between sampling
    """

    def __init__(self,  ip="127.0.0.1",
                        iface="lan",
                        username="admin", 
                        password="admin", 
                        records=[],
                        max_consec_errors=50,
                        logger=None,
                        session_manager=None,
                        delay=0.1,
                        dcmi_power=False,
                        nvidia=-1,
                        g2 = -1,
                        include_nvidia_in_tot_power = False,
                        debug=False):

        self.ip         = ip
        self.iface      = iface
        self.username   = username
        self.password   = password
        self.records    = records
        self.max_consec_errors = max_consec_errors
        self.delay      = delay
        self.logger     = logger
        self.session_manager = session_manager
        self.dcmi_power = dcmi_power
        self.nvidia     = nvidia
        self.g2         = g2
        self.include_nvidia_in_tot_power = include_nvidia_in_tot_power
        self.connected  = False
        self.consec_ipmi_errors = 0
        self.consec_nvid_errors = 0
        self.interface  = None
        self.connection = None
        self.device_id  = None
        self.reservation_id = None
        self.sensors    = []
        self.debug      = debug

    def run_ipmi(self, event):
        """
        This function will run a loop sampling the requested IPMI sensors with a 
        delay between samples.
        """
        if not self.connected:
            raise Exception("ERR: Not connected to the IPMI interface.")
  
        if len(self.sensors)==0:
            self.get_sensors()

        if self.logger:
            descriptions = self.get_sensor_descriptions()
            for descr in descriptions:
                message = "SENSOR: %s %d %d" % (descr['name'], descr['record_id'], descr['number'] )
                if self.logger: self.logger.log(message)

        self.consec_ipmi_errors = 0
   
        # Sample the sensors continuously until 'stop' event
        while not event.is_set():

            if self.dcmi_power:
                #GW: We need to revisit the dcmi impl
                #GW: self._sample_dcmi_power() 
                #GW: if self.nvidia>0:
                #GW:    self._sample_nvidia()
                raise Exception("Not implemented")
            else:
                self._sample_sensors()

            time.sleep( self.delay )    

        if self.debug:
            print("%s: IPMI sensor monitor loop ended." % sys.argv[0])

    def run_nv(self, event):
        """
        This function will run a loop sampling the requested NVidia devices with a
        delay betweem samples.
        """

        # Sample the sensors continuously until 'stop' event
        while not event.is_set():

            self._sample_nvidia()

            time.sleep( self.delay )

        if self.debug:
            print("%s: Nvidia sensor monitor loop ended." % sys.argv[0])

    def run_g2(self, event):
        """
        This function will run a loop sampling the requested GSI G2 devices with a
        delay betweem samples.
        """

        # Sample the sensors continuously until 'stop' event
        while not event.is_set():

            self._sample_g2()

            time.sleep( self.delay )

        if self.debug:
            print("%s: G2 sensor monitor loop ended." % sys.argv[0])

    def connect(self):
        """
        This function will connect to the IPMI interface at its
        IP address and port with provided authentication credentials.
        """
        if self.debug: print("%s: using interface_type=" % type(self).__name__, self.iface)
        self.interface = pyipmi.interfaces.create_interface('ipmitool', interface_type=self.iface)
        self.connection = pyipmi.create_connection(self.interface)
        self.connection.session.set_session_type_rmcp(self.ip, 623)
        self.connection.session.set_auth_type_user(self.username, self.password)
        self.connection.session.establish()
        self.connection.target = pyipmi.Target(ipmb_address=0x20)

        if False:
            for selector in range(1, 6):
                caps = self.connection.get_dcmi_capabilities(selector)
                print('Selector: {} '.format(selector))
                print('  version:  {} '.format(caps.specification_conformence))
                print('  revision: {}'.format(caps.parameter_revision))
                print('  data:     {}'.format(caps.parameter_data))

            rsp = self.connection.get_power_reading(1)

            print('Power Reading')
            print('  current:   {}'.format(rsp.current_power))
            print('  minimum:   {}'.format(rsp.minimum_power))
            print('  maximum:   {}'.format(rsp.maximum_power))
            print('  average:   {}'.format(rsp.average_power))
            print('  timestamp: {}'.format(rsp.timestamp))
            print('  period:    {}'.format(rsp.period))
            print('  state:     {}'.format(rsp.reading_state))
    
            self.interface = pyipmi.interfaces.create_interface('ipmitool', interface_type='lan')
            self.connection = pyipmi.create_connection(self.interface)
            self.connection.target = pyipmi.Target(ipmb_address=0x20)
            self.connection.session.set_session_type_rmcp(self.ip, port=623)
            self.connection.session.set_auth_type_user( self.username, self.password)
            self.connection.session.establish()

        if self.dcmi_power:
            pass #TODO: insert initialization activites here...
        else:
            self.device_id = self.connection.get_device_id()

            if not self.device_id.supports_function('sdr_repository'):
                raise Exception("ERR: IPMI does not support 'sdr_repository' function.")

            self.reservation_id = self.connection.reserve_sdr_repository()
        self.connected = True


    def enumerate_sensors(self):
        """
        This function will enumerate all the sensors available at the IPMI
        interface of the chassis.  It will return the name of the sensor along
        with the sensors record_id identifier."
        """

        if not self.connected:
            raise Exception("ERR: Not connected to the IPMI interface.")

        if self.device_id.supports_function('sdr_repository'):

            print("%s: Using 'sdr_repository' interface" % sys.argv[0])
            iter_fct = self.connection.sdr_repository_entries
        elif device_id.supports_function('sensor'):
            print("%s: Using 'sensor' interface" % sys.argv[0])
            iter_fct = self.connection.device_sdr_entries
        else:
            print("%s: Using default interface" % sys.argv[0])


        if self.debug: print("%s: Enumerating all sensors..." % type(self).__name__)
        for s in iter_fct():
            try:
                #NOTE: decoding might be needed - device_id_string = s.device_id_string.decode("utf-8") 
                device_id_string = s.device_id_string
                print( "%s\t\trecord_id=%d" % (device_id_string, s.id) )
                #print( "%s" % (device_id_string) )
            except:
                if self.debug: traceback.print_exc() 
                pass
        print("Done.")


    def get_sensor_descriptions(self):
        """
        This function will retrieve a full description of sensors, including
        its name, the record_id, and IPMI numeric identifier.
        """

        if len(self.sensors)==0:
            self.get_sensors()

        descriptions = []
        for s in self.sensors:
            descriptions.append( {'name':s.device_id_string, 'record_id':s.id, 'number':s.number } )
    
        return descriptions

    
    def get_sensors(self):
        """
        This function retrieves the sensor object associated with a sensor's record id
        at the IPMI interface.
        """
        
        if len(self.records)==0:
            raise Exception("ERR: No device/sensor records requests.")

        self.sensors=[]
        for record_id in self.records:
            s = self.connection.get_repository_sdr(record_id, self.reservation_id)
            self.sensors.append(s)

        return True


    def _sample_sensors(self):

        for s in self.sensors:

            if self._sample_sensor(s)==False:
                print("%s: Incrementing consec ipmi errors from" % sys.argv[0], self.consec_ipmi_errors)
                self.consec_ipmi_errors += 1

            if self.consec_ipmi_errors >= self.max_consec_errors:
                raise Exception("ERR: Maximum consecutive ipmi errors reached.")

    def _sample_sensor(self,s):

        try:
            number = None
            value = None
            states = None
    
            if s.type is pyipmi.sdr.SDR_TYPE_FULL_SENSOR_RECORD:
                (value, states) = self.connection.get_sensor_reading(s.number)
                number = s.number

                if value is not None:
                    value = s.convert_sensor_raw_to_value(value)
                elif s.type is pyipmi.sdr.SDR_TYPE_COMPACT_SENSOR_RECORD:
                    (value, states) = self.connection.get_sensor_reading(s.number)
                    number = s.number

                self.emit_sdr_list_entry(s.id, number, s.device_id_string, value, states)
                return True

        except pyipmi.errors.CompletionCodeError as e:
            print("%s: CompletionCodeError" % sys.argv[0])
            if s.type in (pyipmi.sdr.SDR_TYPE_COMPACT_SENSOR_RECORD, pyipmi.sdr.SDR_TYPE_FULL_SENSOR_RECORD):
                print('%s: CompletionCodeError: 0x{:04x} | {:3d} | {:18s} | ERR: CC=0x{:02x}'.format( sys.argv[0], s.id, s.number, s.device_id_string, e.cc))
            return False

        except:
            print("%s: Sample Sensor Error:" % sys.argv[0], traceback.print_exc())
            return False            

        finally:
            pass

    def _sample_nvidia(self):
        try:
            if self.debug: print("About to call nvidia-smi for power...")

            cmd = "nvidia-smi --query-gpu=index,power.draw --format=csv"
            if self.debug: print("running nvidia-smi command", cmd)
            stream = os.popen(cmd)
            outp = stream.read()
            if self.debug: print("result of cmd=", outp)

            # parse csv shape response
            lines = [ ln for ln in outp.split('\n') if ln.strip()!="" ]
            if self.debug: print("nvidia lines", lines, len(lines), self.nvidia)
            if len(lines)!= self.nvidia + 2:
                errstr = "ERROR: Could not find %d Nvidia boards but found %d" % ( self.nvidia, len(lines)-1 )
                raise Exception(errstr) 

            powers = [ (int(ln.strip().split(",")[0]), \
                        float(ln.strip().split(",")[1].strip().split()[0] )) \
                        for ln in lines[1:] ]
            if self.debug: print("nvidia power(s)", powers)

            self.emit_nvidia_power( powers )

        except:
            print("Sample nvidia power error:", sys.exc_info()[0])
            traceback.print_exc()

    def emit_nvidia_power(self, powers):
        for power in powers:
            nv_id, value = power
            message = "%d : %s" % ( nv_id, value)
            if self.logger:
                dt = self.logger.log(message)
            else:
                dt = datetime.datetime.now()
            if self.session_manager:
                self.session_manager.nvidia_sensor(dt, nv_id, float(value) )
            if self.debug:
                message = "nvidia: %d : %s" % ( nv_id, value)
                print(message)

    def emit_g2_power(self, power):
            message = "%d : %f" % ( self.g2, power)
            if self.logger:
                dt = self.logger.log(message)
            else:
                dt = datetime.datetime.now()
            if self.session_manager:
                self.session_manager.g2_sensor(dt, self.g2, power )
            if self.debug:
                message = "g2: %d : %f" % ( self.g2, power)
                print(message)

    def _sample_g2(self):
        try:
            if self.debug: print("About to call gsi_tool for power...")

            addr = "apu-%02d" % self.g2
            cmd = "gsi_tool info %s" % addr
            if self.debug: print("running gsi_tool command:", cmd)
            stream = os.popen(cmd)
            outp = stream.read()
            if self.debug: print("result of cmd=", outp)

            matches = re.findall(GSI_TOOL_POWER_REGEX,outp)
            if self.debug: print("regex matches:", matches)
       
            power = float(matches[0])
            self.emit_g2_power( power )

        except:
            print("Sample g2 power error:", sys.exc_info()[0])
            traceback.print_exc()

    def _sample_dcmi_power(self):
        try:

            if self.debug: print("About to call dcmi get_power_readings...")
            rsp = self.connection.get_power_reading(1)
            if self.debug: 
                print("get_power_readings called completed.")
                print('Power Reading')
                print('  current:   {}'.format(rsp.current_power))
                print('  minimum:   {}'.format(rsp.minimum_power))
                print('  maximum:   {}'.format(rsp.maximum_power))
                print('  average:   {}'.format(rsp.average_power))
                print('  timestamp: {}'.format(rsp.timestamp))
                print('  period:    {}'.format(rsp.period))
                print('  state:     {}'.format(rsp.reading_state))
               
            self.emit_dcmi_power(-1, "%d" % rsp.current_power)

        except:
            print("Sample dcmi power error:", sys.exc_info()[0])
            traceback.print_exc()

        finally:
            pass 

    def emit_dcmi_power(self, record_id, value):
        if self.logger:
            message = "%d : %s" % ( record_id, value)
            dt = self.logger.log(message)
        elif self.debug:
            message = "0x%04x | %9s " % (record_id, number, id_string, value, states)
            print(message)
        else:
            dt = datetime.datetime.now()

        if self.session_manager:
            self.session_manager.sensor(dt, record_id, float(value) )


    def emit_sdr_list_entry(self, record_id, number, id_string, value, states):
        """This function will output the data associated with a sensor
        either to a logger object or standard output, in a standard format.
        """

        if number:
            number = str(number)
        else:
            number = 'na'
        if states:
            states = hex(states)
        else:
            states = 'na'

        if self.logger: 
            message = "%d : %s" % ( record_id, value)
            if self.debug: print("%s: emitting sensor value to logger" % sys.argv[0], message)
            dt = self.logger.log(message)
        elif self.debug:
            message = "0x%04x | %3s | %-18s | %9s | %s" % (record_id, number, id_string, value, states)
            dt = datetime.datetime.now()
            print(dt, message)
        else:
            dt = datetime.datetime.now()

        if self.session_manager:
            self.session_manager.sensor(dt, record_id, float(value) )

#
# To run the unit tests below for the IpmiMon class, type "python ipmimon.py"
#
if __name__ == "__main__":

    ipmimon = IpmiMon(  ip="192.168.99.61", 
                        iface="lan", # try also 'lanplus'
                        username="ADMIN",
                        password="ADMIN",
                        records=[5029],
                        delay=0.05, 
                        debug=True)
    ipmimon.connect()
    #ipmimon.enumerate_sensors()
    ipmimon.run()


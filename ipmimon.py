import pyipmi
import pyipmi.interfaces
import time
import os

class IpmiMon:

	def __init__(self, 	ip="127.0.0.1", 
						username="admin", 
						password="admin", 
						records=[],
						max_consec_errors=2,
						delay=0.1,
						logger=None):

		self.ip 		= ip
		self.username 	= username
		self.password 	= password
		self.records 	= records
		self.max_consec_errors = max_consec_errors
		self.delay 		= delay
		self.logger		= logger
	
	def run(self):
		
		self._get_sensors()

		self.consec_errors = 0
	
		while True:

			self._sample_sensors()

			time.sleep( self.delay )	


	def _get_sensors(self):
	
		if len(self.records)==0:
			raise Exception("ERR: No device/sensor records requests.")
		
		self.interface = pyipmi.interfaces.create_interface('ipmitool', interface_type='lan')
		self.connection = pyipmi.create_connection(self.interface)
		self.connection.target = pyipmi.Target(ipmb_address=0x20)
		self.connection.session.set_session_type_rmcp(self.ip, port=623)
		self.connection.session.set_auth_type_user( self.username, self.password)
		self.connection.session.establish()

		self.device_id = self.connection.get_device_id()

		if not self.device_id.supports_function('sdr_repository'):
			raise Exception("ERR: IPMI does not support 'sdr_repository' function.")

		reservation_id = self.connection.reserve_sdr_repository()

		self.sensors=[]
		for record_id in self.records:
			s = self.connection.get_repository_sdr(record_id, reservation_id)
			self.sensors.append(s)

		return True

	def _sample_sensors(self):

		for s in self.sensors:

			if self._sample_sensor(s)==False:
				self.consec_errors += 1

			if self.consec_errors >= self.max_consec_errors:
				raise Exception("ERR: Maximum consecutive errors reached.")

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
				return value

		except pyipmi.errors.CompletionCodeError as e:
			if s.type in (pyipmi.sdr.SDR_TYPE_COMPACT_SENSOR_RECORD, pyipmi.sdr.SDR_TYPE_FULL_SENSOR_RECORD):
				print('0x{:04x} | {:3d} | {:18s} | ERR: CC=0x{:02x}'.format( s.id, s.number, s.device_id_string, e.cc))
			return False

		finally:
			pass

	def emit_sdr_list_entry(self, record_id, number, id_string, value, states):
		if number:
			number = str(number)
		else:
			number = 'na'
		if states:
			states = hex(states)
		else:
			states = 'na'

		message = "0x%04x | %3s | %-18s | %9s | %s" % (record_id, number, id_string, value, states)
		if self.logger: self.logger.log(message)
		else: print(message)


if __name__ == "__main__":

	ipmimon = IpmiMon( 	ip="192.168.99.35", 
						username="admin",
						password="admin",
						records=[18,20] )

	ipmimon.run()


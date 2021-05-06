import pyipmi
import pyipmi.interfaces

# Supported interface_types for ipmitool are: 'lan' , 'lanplus', and 'serial-terminal'
interface = pyipmi.interfaces.create_interface('ipmitool', interface_type='lan')

connection = pyipmi.create_connection(interface)

connection.target = pyipmi.Target(ipmb_address=0x20)

#connection.target = pyipmi.Target(0x82)
#connection.target.set_routing([(0x81,0x20,0),(0x20,0x82,7)])

#GW connection.session.set_session_type_rmcp('10.0.0.1', port=623)
connection.session.set_session_type_rmcp('192.168.99.35', port=623)
connection.session.set_auth_type_user('admin', 'admin')
connection.session.establish()

device_id = connection.get_device_id()
print(type(device_id),device_id)

if device_id.supports_function('sdr_repository'):
	iter_fct = connection.sdr_repository_entries
elif device_id.supports_function('sensor'):
	iter_fct = connection.device_sdr_entries

def print_sdr_list_entry(record_id, number, id_string, value, states):
	if number:
		number = str(number)
	else:
		number = 'na'
    
	if states:
		states = hex(states)
	else:
		states = 'na'
    
	print("0x%04x | %3s | %-18s | %9s | %s" % (record_id, number, id_string, value, states))

for s in iter_fct():
	try:
		number = None
		value = None
		states = None

		if s.type is pyipmi.sdr.SDR_TYPE_FULL_SENSOR_RECORD:
			(value, states) = connection.get_sensor_reading(s.number)
			print("FS", s.number, value, states)
			number = s.number
			if value is not None:
				value = s.convert_sensor_raw_to_value(value)
				print("FS AFTER CONVERT", value)
			elif s.type is pyipmi.sdr.SDR_TYPE_COMPACT_SENSOR_RECORD:
				(value, states) = connection.get_sensor_reading(s.number)
				print("CS", s.number, value, states)
				number = s.number
            
			print_sdr_list_entry(s.id, number, s.device_id_string,
                                 value, states)
        
	except pyipmi.errors.CompletionCodeError as e:
		if s.type in (pyipmi.sdr.SDR_TYPE_COMPACT_SENSOR_RECORD, pyipmi.sdr.SDR_TYPE_FULL_SENSOR_RECORD):
			print('0x{:04x} | {:3d} | {:18s} | ERR: CC=0x{:02x}'.format( s.id, s.number, s.device_id_string, e.cc))

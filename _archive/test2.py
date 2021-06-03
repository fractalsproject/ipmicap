import pyipmi
import pyipmi.interfaces
import time

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

print("GETTING DEVICE ID")
device_id = connection.get_device_id()
print(type(device_id),device_id)

print("CHECKING SUPPORT")
if device_id.supports_function('sdr_repository'):
	print("AFTER SDR REP")
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

if False:
	print("ONE ITER")
	count=0
	for s in iter_fct():
		print("DONE ONE ITER")
		count = count + 1
		if count>1: break

print("\n")
print("GETTING RESERV")
reservation_id = connection.reserve_sdr_repository()
print("RESERV", reservation_id)
print("\n")

s = connection.get_repository_sdr(18, reservation_id)
print(s)

sensors = [s]

def sample_sensor(s):
    try:
        number = None
        value = None
        states = None

        if s.type is pyipmi.sdr.SDR_TYPE_FULL_SENSOR_RECORD:
            (value, states) = connection.get_sensor_reading(s.number)
            number = s.number

            if value is not None:
                value = s.convert_sensor_raw_to_value(value)
            elif s.type is pyipmi.sdr.SDR_TYPE_COMPACT_SENSOR_RECORD:
                (value, states) = connection.get_sensor_reading(s.number)
                number = s.number

            print_sdr_list_entry(s.id, number, s.device_id_string,
                                 value, states)
            return value

    except pyipmi.errors.CompletionCodeError as e:
        if s.type in (pyipmi.sdr.SDR_TYPE_COMPACT_SENSOR_RECORD, pyipmi.sdr.SDR_TYPE_FULL_SENSOR_RECORD):
            print('0x{:04x} | {:3d} | {:18s} | ERR: CC=0x{:02x}'.format( s.id, s.number, s.device_id_string, e.cc))
        return None

    finally:
        return None


if len(sensors)>0:
    print("Found sensors of interest.")

    print("Starting continuos sampling of sensors...")

    while True:
        try:
            for s in sensors:
                val = sample_sensor(s)
                print(val)
        except:
            print("sensor read error")

        time.sleep(0.25)

else:
    print("Could not locate sensors of interst.")


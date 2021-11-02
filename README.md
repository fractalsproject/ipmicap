# IPMICAP

## Introduction

The Intelligent Platform Management Interface (IPMI) is an industry standard for remote management of datacenter servers.  Dedicated electronics built into a modular server chassis implements IPMI capabilites such as remote power management and sensor monitoring ( such as power monitoring. ) IPMICAP is a logging utility for capturing sensor data that is made available via IPMI.

## Prerequisites

IPMICAP was developed and tested using the following:

* Ubuntu 18.04.

* Anaconda Python ( using a python=37 conda environment )

* "ipmitool" via apt-get, version 1.8.18

* The python package dependencies are specified in the requirements.txt file

## Installation

* Install a compatible version of "ipmitool" ( we used 1.8.18 )

* Clone this repository.

* Install the python dependencies via "pip install -r requirements.txt"

## How To Run

### Enable and Configure Your Chassis IPMI Interface

* You need to enable your chassis IPMI interface using a compatible IPMICFG tool.

* You will need the IPMI interface's ip address and user/password authentication credentials going forward.

## Enumerate Your Sensors

* Run the following:  "python ipmicap  --ip <IPMI_IP_ADDRESS>  --enumerate"

* This will connect to the IPMI interface and enumerate all available sensors (the name and the record id of each sensor.)

* Choose the sensors you want to capture.

## Capture and Log Sensor Data To A File

* Run the following: "python ipmicap  --ip <IPMI_IP_ADDRESS>  --records [RECORD_ID_1 RECORD_ID_2 ...]

* This will create a log file under /tmp/ and will log the timestamped sensor data values to that file at 1 second sampling intervals.  Use the "--delay" argument to change the delay.

## Capture and Log Sensor Data And Listen For Custom Log Messages

* Run the following: "python ipmicap  --ip <IPMI_IP_ADDRESS>  --records [RECORD_ID_1 RECORD_ID_2 ...]  --listen [LISTEN_PORT]

* In addition to logging sensor data to a file, this will start a web service at the LISTEN_PORT and will log those messages to the file.

* To write a custom log message during capture, send a GET request in this format:  http://[MACHINE]:[LISTEN_PORT]/log?message=[CUSTOM_MESSAGE] where MACHINE is the name or ip address of the machine running ipmicap.py, LISTEN_PORT is a port of your choice, and CUSTOM_MESSAGE is any urlencoded string.

## BigANN T3 Competition

The BigANN benchmarks T3 track leverages IPMICAP for power consumption benchmarks.

Depending on the chassis/motherboard, you will need to start the server in one of the following ways.

### Advantech Chassis

To monitor the power consumption for Advantech chassis/motherboard run the following:

```python ipmicap --ip <IPMI_IP_ADDRESS> --records [RECORD_ID_1 RECORD_ID_2 ... ] --usernmae <NAME> --password <PASSWORD> --listen [LISTEN_PORT] --sessions```

where:
* IPMI_IP_ADDRES = the ip address of the machine's IPMI interface
* RECORD_ID_X = the record ID of the sensor
* NAME = the username credentials to the IPMI interface
* PASSWORD = the password credentials to the IPMI interface
* LISTEN_PORT = any available port from which to listen to API requests

Make sure to provide the following flags when you run the BigANN compevaluation run script (run.py):  "--t3 --power-capture <IP>:<PORT>:10" where IP and PORT are associated with your IPMICAP server instance.

### Supermicro Chassis

To monitor the power consumption for a Supermicro chassis/motherboard run the following:

```python ipmicap --ip <IPMI_IP_ADDRESS> --dcmi-power --usernmae <NAME> --password <PASSWORD> --listen [LISTEN_PORT] --sessions```

where:
* IPMI_IP_ADDRES = the ip address of the machine's IPMI interface
* NAME = the username credentials to the IPMI interface
* PASSWORD = the password credentials to the IPMI interface
* LISTEN_PORT = any available port from which to listen to API requests

Make sure to provide the following flags when you run the BigANN compevaluation run script (run.py):  "--t3 --power-capture <IP>:<PORT>:10" where IP and PORT are associated with your IPMICAP server instance.

# TODO

* Allow user to specify path to log file
* urldecode all URL parameters
* Combine URL parameters into one line of log file
* Cleaner notebook examples

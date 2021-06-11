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
* You will need the IPMI interface's ip address and user/password authentication credentials.

## Enumerate Your Sensors

* Run the following:  "python ipmicap --ip <IPMI_IP_ADDRESS> --enumerate"
* This will connect to the IPMI interface and enumerate all available sensors (the name and the record id of each sensor.)
* Choose the sensor you want to capture.

## Capture and Log Sensor Data To A File

* Run the following: "python ipmicap --ip <IPMI_IP_ADDRESS> --records [RECORD_ID_1 RECORD_ID_2 ...]
* This will create a log file under /tmp/ and will log the timestamped sensor data values to that file at 1 second sampling intervals.  Use the "--delay" argument to change the delay.

## Capture and Log Sensor Data And Listen For Custom Log Messages
* Run the following: "python ipmicap --ip <IPMI_IP_ADDRESS> --records [RECORD_ID_1 RECORD_ID_2 ...] --listen [LISTEN_PORT]
* In addition to logging sensor data to a file, this will start a web service at the LISTEN_PORT and will log those messages to the file.
* To write a custom log message, send a GET request in this format:  http://[MACHINE]:[LISTEN_PORT]/log?message=[CUSTOM_MESSAGE] where MACHINE is the name or ip address of the machine running ipmicap.py, LISTEN_PORT is a port of your choice, and CUSTOM_MESSAGE is any urlencoded string.

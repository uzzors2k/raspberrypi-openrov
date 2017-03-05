#!/usr/bin/python
import struct
import time
import sys
import signal

# Controller to read from
infile_path = "/dev/input/js0"

##############################################################
# Define events
JS_EVENT_BUTTON = 0x01		# button pressed/released
JS_EVENT_AXIS = 0x02		# joystick moved
JS_EVENT_INIT = 0x80		# initial state of device

JS_BUTTON_ON = 0x01
JS_BUTTON_OFF = 0x00

# Define Dual Axis joystick bindings
DUAL_SHOCK_LEFT_STICK_HORS = 0
DUAL_SHOCK_LEFT_STICK_VERT = 1
DUAL_SHOCK_RIGHT_STICK_VERT = 2
DUAL_SHOCK_RIGHT_STICK_HORS = 3

DUAL_SHOCK_BUTTON_L1 = 10
DUAL_SHOCK_BUTTON_L2 = 8
DUAL_SHOCK_BUTTON_L3 = 1
DUAL_SHOCK_BUTTON_R1 = 11
DUAL_SHOCK_BUTTON_R2 = 9
DUAL_SHOCK_BUTTON_R3 = 2

DUAL_SHOCK_BUTTON_SELECT = 0
DUAL_SHOCK_BUTTON_START = 3
DUAL_SHOCK_BUTTON_PS = 16

DUAL_SHOCK_BUTTON_DIR_UP = 4
DUAL_SHOCK_BUTTON_DIR_DOWN = 6
DUAL_SHOCK_BUTTON_DIR_LEFT = 7
DUAL_SHOCK_BUTTON_DIR_RIGHT = 5

DUAL_SHOCK_BUTTON_DIR_TRIANGLE = 12
DUAL_SHOCK_BUTTON_DIR_CIRCLE = 13
DUAL_SHOCK_BUTTON_DIR_CROSS = 14
DUAL_SHOCK_BUTTON_DIR_SQUARE = 15

##############################################################

##############################################################

# Capture interrupt signal (Ctrl-C). Close the TCP connection
def handler(signum, frame):
	print 'Shutting down...'
	in_file.close()
	sys.exit(0)
	
signal.signal(signal.SIGINT, handler)

##############################################################

#long int, long int, unsigned short, unsigned short, unsigned int
FORMAT = 'IhBB'
EVENT_SIZE = struct.calcsize(FORMAT)

#open file in binary mode
in_file = open(infile_path, "rb")

event = in_file.read(EVENT_SIZE)

while event:
    (time, value, type, number) = struct.unpack(FORMAT, event)
	
    if type != 0 or code != 0 or value != 0:
        #print("Event type {0}, number {1}, value: {2} at time {3}" \
		#	.format(type, number, value, time))
		
		# Filter button events
		if (type == JS_EVENT_BUTTON):
			print("Button Event: value {0}, axis/button: {1}" \
				.format(value, number))
		
		# Filter axis movements for sticks
		if (type == JS_EVENT_AXIS):
			# Only allow updates from certain axes
			if ((number == DUAL_SHOCK_LEFT_STICK_VERT) \
				or (number == DUAL_SHOCK_LEFT_STICK_HORS) \
				or (number == DUAL_SHOCK_RIGHT_STICK_VERT) \
				or (number == DUAL_SHOCK_RIGHT_STICK_HORS)):
					print("Update Event: value {0}, axis/button: {1}" \
						.format(value, number))
		
    else:
        # Events with code, type and value == 0 are "separator" events
        print("===========================================")
	
    event = in_file.read(EVENT_SIZE)

in_file.close()
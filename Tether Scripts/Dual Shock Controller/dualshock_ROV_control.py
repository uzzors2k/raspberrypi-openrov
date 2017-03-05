#!/usr/bin/python
#
# dualshock_ROV_control.py
# Connect a PS3 Dual Shock Controller via Bluetooth
# and read the button states in Python. Send
# translated ROV movement commands over network
# to the ROV controller.
#
# Author : Eirik Taylor
# Date   : 04/02/2016
#
#	Packet Format:
#
# SET_VIDEO_RECORD:<0-1>
# SET_LIGHT:<0 to 512>
# 
# ROTATE_ROV_YAW:<-512 to 512>
# 
# TRANSLATE_ROV_X:<-512 to 512>
# TRANSLATE_ROV_Y:<-512 to 512>
# TRANSLATE_ROV_Z:<-512 to 512>
# 
# ROTATE_CAMERA_YAW:<-512 to 512>
# ROTATE_CAMERA_PITCH:<-512 to 512>
#
# SYSTEM_SHUTDOWN:<0-1>
#
#	IO pinning:
#
#	GPIO18 - > Switch
#	GPIO23 - > Status LED
#	GPIO24 - > Recording LED
#
#=================================

#!/usr/bin/python
import struct
import time
import sys
import signal
import socket
import subprocess
from multiprocessing import Process, Queue
import RPi.GPIO as GPIO

# Controller to read from
joystickPath = "/dev/input/js0"

# Message which defaults all settings on the ROV
defaultMessagePacket = ("<SET_VIDEO_RECORD:0;SET_LIGHT:0;ROTATE_ROV_YAW:0; \
						TRANSLATE_ROV_X:0;TRANSLATE_ROV_Y:0; \
						TRANSLATE_ROV_Z:0;ROTATE_CAMERA_YAW:0; \
						ROTATE_CAMERA_PITCH:0;SYSTEM_SHUTDOWN:0;>")
						
shutDownMessagePacket = ("<SYSTEM_SHUTDOWN:1;>")

##################################################################################
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

##################################################################################

# Capture interrupt signal (Ctrl-C). Close the TCP connection
def handler(signum, frame):
	print 'Shutting down...\n'
	s.close()
	GPIO.cleanup()
	sys.exit(0)
	
signal.signal(signal.SIGINT, handler)

##################################################################################

def shutdownEverything():
	command = "/usr/bin/sudo /sbin/shutdown -h now"
	process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]
	print output
	print 'Shutting down system...\n'
	s.close()
	GPIO.cleanup()
	sys.exit(0)

##################################################################################

def noBluetoothUnitReboot():
	command = "/usr/bin/sudo /sbin/reboot"
	process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]
	print output
	print 'Rebooting system...\n'
	sys.exit(1)

##################################################################################

def limitAndConvertToFloatRatio(input, base):
	# Limit to [1.0, -1.0]
	if (input > base):
		input = base
	elif (input < -base):
		input = -base
	
	# Convert an input to a float between 0.0 and 1.0
	return float(input) / float(base)

##################################################################################

def parseJoystickMovements(messageOutQueue):
	# Various settings
	Analog_stick_max_range = 512
	Reduced_analog_factor = 4
	LED_brightness_step = 128
	Camera_pitch_step = 32

	# Controller state variables
	LED_brightness = 256
	Recording_state = 0
	ROV_translateX = 0
	ROV_translateY = 0
	ROV_translateZ = 0
	ROV_rotateZ = 0
	CAMERA_pitch = 0
	CAMERA_yaw = 0
	Slow_movement_modifier = True
	
	# Specifics for /dev/input/
	#long int, long int, unsigned short, unsigned short, unsigned int
	FORMAT = 'IhBB'
	EMPTY_STRUCT_STRING = '\x00\x00\x00\x00\x00\x00\x00\x00'
	EVENT_SIZE = struct.calcsize(FORMAT)
	
	joystickConnected = False
	joystickHasBeenConnected = False
	try:
		#open file in binary mode
		in_file = open(joystickPath, "rb")
		joystickConnected = True
		joystickHasBeenConnected = True
	except IOError:
		joystickConnected = False
	
	while True:
		if joystickConnected:
			################# Read from the IO stream ##########################
			try:
				# Read from the joystick stream
				event = in_file.read(EVENT_SIZE)
			except IOError:
				event = EMPTY_STRUCT_STRING
				joystickConnected = False
			(evnt_time, value, type, number) = struct.unpack(FORMAT, event)
				
			# Do something based on the event type
			if type != 0 or value != 0:

				# Filter button events
				if (type == JS_EVENT_BUTTON):

					# ROV LED control
					if (number == DUAL_SHOCK_BUTTON_DIR_TRIANGLE):
						if (value == JS_BUTTON_ON):
							LED_brightness = LED_brightness + LED_brightness_step
							#print 'ROV LEDs brighter\n'
							if (LED_brightness > 512):
								LED_brightness = 512
					elif (number == DUAL_SHOCK_BUTTON_DIR_CROSS):
						if (value == JS_BUTTON_ON):
							LED_brightness = LED_brightness - LED_brightness_step
							#print 'ROV LEDs dimmer\n'
							if (LED_brightness < 0):
								LED_brightness = 0
					
					# Camera pitch
					if (number == DUAL_SHOCK_BUTTON_DIR_UP):
						if (value == JS_BUTTON_ON):
							CAMERA_pitch = CAMERA_pitch + Camera_pitch_step
							#print 'Camera tilted higher\n'
							if (CAMERA_pitch > 512):
								CAMERA_pitch = 512
					elif (number == DUAL_SHOCK_BUTTON_DIR_DOWN):
						if (value == JS_BUTTON_ON):
							CAMERA_pitch = CAMERA_pitch - Camera_pitch_step
							#print 'ROV tilted lower\n'
							if (CAMERA_pitch < -512):
								CAMERA_pitch = -512
					
					# Camera yaw
					if (number == DUAL_SHOCK_BUTTON_DIR_RIGHT):
						if (value == JS_BUTTON_ON):
							CAMERA_yaw = CAMERA_yaw + Camera_pitch_step
							#print 'Camera turned right\n'
							if (CAMERA_yaw > 512):
								CAMERA_yaw = 512
					elif (number == DUAL_SHOCK_BUTTON_DIR_LEFT):
						if (value == JS_BUTTON_ON):
							CAMERA_yaw = CAMERA_yaw - Camera_pitch_step
							#print 'ROV turned left\n'
							if (CAMERA_yaw < -512):
								CAMERA_yaw = -512
					
					# Center both camera axis
					if (number == DUAL_SHOCK_BUTTON_SELECT):
						if (value == JS_BUTTON_ON):
							CAMERA_pitch = 0
							CAMERA_yaw = 0
							#print 'Camera centered\n'
							
					# Change the video recording state
					if (number == DUAL_SHOCK_BUTTON_START):
						if (value == JS_BUTTON_ON):
							if (Recording_state == 0):
								Recording_state = 1
								GPIO.output(24, True)
								#print 'Recording enabled\n'
							else:
								Recording_state = 0
								GPIO.output(24, False)
								#print 'Recording disabled\n'
								
					# Reduce the amplitude of the analog stick movements
					if ((number == DUAL_SHOCK_BUTTON_L2) or (number == DUAL_SHOCK_BUTTON_R2)):
						if (value == JS_BUTTON_ON):
							Slow_movement_modifier = False
							#print 'Normal speed mode\n'
						else:
							Slow_movement_modifier = True
							#print 'Reduced speed mode\n'
				
				# Filter axis movements for sticks
				if (type == JS_EVENT_AXIS):
					# Only allow updates from certain axes
					if ((number == DUAL_SHOCK_LEFT_STICK_VERT) \
						or (number == DUAL_SHOCK_LEFT_STICK_HORS) \
						or (number == DUAL_SHOCK_RIGHT_STICK_VERT) \
						or (number == DUAL_SHOCK_RIGHT_STICK_HORS)):
							
							max_stick = Analog_stick_max_range
							if (Slow_movement_modifier):
								# Reduce speed
								max_stick = max_stick / Reduced_analog_factor
							
							# ROV Yaw control
							if (number == DUAL_SHOCK_RIGHT_STICK_HORS):
								#print 'ROV Yaw\n'
								ROV_rotateZ = int(max_stick * limitAndConvertToFloatRatio(value, 32767))
								
							# ROV Forward thrust control
							if (number == DUAL_SHOCK_RIGHT_STICK_VERT):
								#print 'ROV move forward/backward\n'
								ROV_translateX = int(max_stick * limitAndConvertToFloatRatio(value, 32767))
								
							# ROV Upward thrust control
							if (number == DUAL_SHOCK_LEFT_STICK_VERT):
								#print 'ROV move up/down\n'
								ROV_translateZ = int(max_stick * limitAndConvertToFloatRatio(value, 32767))
								
							# ROV Strafe control
							if (number == DUAL_SHOCK_LEFT_STICK_HORS):
								#print 'ROV move up/down\n'
								ROV_translateY = int(max_stick * limitAndConvertToFloatRatio(value, 32767))
								

				# Create a packet from the joystick data
				messagePacket = ("<SET_VIDEO_RECORD:{};SET_LIGHT:{};ROTATE_ROV_YAW:{}; \
								TRANSLATE_ROV_X:{};TRANSLATE_ROV_Y:{}; \
								TRANSLATE_ROV_Z:{};ROTATE_CAMERA_YAW:{}; \
								ROTATE_CAMERA_PITCH:{};SYSTEM_SHUTDOWN:0;>"
								.format(Recording_state, LED_brightness,
								ROV_rotateZ, ROV_translateX, ROV_translateY,
								ROV_translateZ, CAMERA_yaw, CAMERA_pitch))
									
			else:
				# Events with code, type and value == 0 are "separator" events
				messagePacket = defaultMessagePacket
				
			############ Push the new message onto the queue ####################
			try:
				messageOutQueue.put(messagePacket, False)
			except Queue.Full:
				# Don't really care, new data is more important
				pass
			
			#####################################################################
		else:
			############ Shutdown once connection is lost #######################
			if joystickHasBeenConnected:
				try:
					messageOutQueue.put(shutDownMessagePacket, False)
				except Queue.Full:
					# Don't really care, new data is more important
					pass
			
			else:
			########### Need to try reconnecting... #############################
				try:
					#open file in binary mode
					in_file = open(joystickPath, "rb")
					joystickConnected = True
					joystickHasBeenConnected = True
				except IOError:
					joystickConnected = False
			
##################################################################################

# Check if the bluetooth dongle is initialized

print 'Checking for connected bluetooth devices'

# Execute the command to list connected devices, and collect the result
bluetoothListDevicesCommand='hcitool dev'
process = subprocess.Popen(bluetoothListDevicesCommand.split(), stdout=subprocess.PIPE)
output = process.communicate()[0]
print 'Connected devices: ' + output

# Look for hci0 in the result string
desiredResult='hci0'
result = output.find(desiredResult)

# If not found, reboot after a short timeout
if (result == -1):
	print 'No bluetooth device found, rebooting in 20 seconds...'
	time.sleep(20)
	noBluetoothUnitReboot()

# Setup GPIO pins
#	GPIO18 - > Switch (active low)
#	GPIO23 - > Status LED
#	GPIO24 - > Recording LED
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)

GPIO.output(23, False)
GPIO.output(24, False)

# Input update period [s]
button_delay = 0.1

# Number of update cycles to wait before changing LED state
LED_BLINK_RATE = 5
ledBlinkCounter = 0
ledBlinkState = False

# Connection definitions
TCP_IP = '172.28.0.12'
TCP_PORT = 5005
BUFFER_SIZE = 128

# Connect to the remote unit, and initialize all settings
socketConnected = False
try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((TCP_IP, TCP_PORT))
	s.send(defaultMessagePacket)
	socketConnected = True
	GPIO.output(23, True)
except:
	socketConnected = False

##############################################################

joystickMessageQueue = Queue()
joystickProcess = Process(target = parseJoystickMovements, args=(joystickMessageQueue,))
joystickProcess.start()

##############################################################

# Initialized here so the last packet is remembered
sendPacket = defaultMessagePacket

print 'Starting...'

# Main thread handles the socket connection
while True:

	# Read from the queue until it is empty, we only want the last message received
	while not joystickMessageQueue.empty():
		try:
			sendPacket = joystickMessageQueue.get(False)
		except Queue.Empty:
			pass
	
	# Show what we've got
	#print sendPacket
	
	# Try connecting to remote machine if connection is lost
	if (not socketConnected):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((TCP_IP, TCP_PORT))
			socketConnected = True
			GPIO.output(23, True)
		except:
			socketConnected = False
			# Blink status LED
			if (ledBlinkCounter > LED_BLINK_RATE):
				ledBlinkCounter = 0
				ledBlinkState = not ledBlinkState
				GPIO.output(23, ledBlinkState)
			else:
				ledBlinkCounter = ledBlinkCounter + 1
	else:
		try:
			s.send(sendPacket)
			if (sendPacket == shutDownMessagePacket):
				# Shutdown only once the message is sent!
				print 'Shutting down system due to controller disconnect...'
				shutdownEverything()
		except:
			socketConnected = False
	
	# Check if the shutdown button has been pressed
	if (GPIO.input(18) == 0):
		print 'Shutting down system due to off button pressed...'
		if (socketConnected):
			try:
				joystickMessageQueue.put(shutDownMessagePacket, False)
			except Queue.Full:
				# Don't really care, new data is more important
				pass
		else:
			shutdownEverything()
	
	time.sleep(button_delay)

#!/usr/bin/python
#
# wii_remote_ROV_control.py
# Connect a Nintendo Wii Remote via Bluetooth
# and read the button states in Python. Send
# translated ROV movement commands over network
# to the ROV controller.
#
# Author : Eirik Taylor
# Date   : 06/12/2015
#
# Number       Binary       Button
#=================================
#     1    00000000000001   2
#     2    00000000000010   1
#     4    00000000000100   B
#     8    00000000001000   A
#    16    00000000010000   MINUS
#   128    00000010000000   HOME
#   256    00000100000000   DOWN
#   512    00001000000000   UP
#  1024    00010000000000   RIGHT
#  2048    00100000000000   LEFT
#  4096    01000000000000   PLUS
#=================================
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
#=================================

import cwiid
import time
import socket
import signal
import sys

# Capture interrupt signal (Ctrl-C). Close the TCP connection
def handler(signum, frame):
	print 'Shutting down...'
	s.close()
	if (wiiMoteIsConnected):
		exit(wii)
	sys.exit(0)
	
signal.signal(signal.SIGINT, handler)

# Input update frequency
button_delay = 0.1

LED_brightness_step = 128

# Connection definitions
TCP_IP = '192.168.1.12'
TCP_PORT = 5005
BUFFER_SIZE = 128

# Controller state variables
LED_brightness = 256
Recording_state = 0
ROV_translateX = 0
ROV_translateZ = 0
ROV_rotateZ = 0

# Message which defaults all settings on the ROV
defaultMessagePacket = ("<SET_VIDEO_RECORD:0;SET_LIGHT:0;ROTATE_ROV_YAW:0; \
						TRANSLATE_ROV_X:0;TRANSLATE_ROV_Y:0; \
						TRANSLATE_ROV_Z:0;ROTATE_CAMERA_YAW:0; \
						ROTATE_CAMERA_PITCH:0;>")

# Various state variables
wiiMoteIsConnected = False
recordButtonDepressed = False
lightButtonDepressed = False

# Connect to the remote unit, and initialize all settings
socketConnected = False
try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((TCP_IP, TCP_PORT))
	s.send(defaultMessagePacket)
	socketConnected = True
except:
	socketConnected = False

print 'Press 1 + 2 on your Wii Remote now ...'
time.sleep(1)
 
while True:
	time.sleep(button_delay) 
	
	# If connected to wii, make a valid message packet, otherwise make a default one
	if (wiiMoteIsConnected):
		buttons = wii.state['buttons']
		
		# If Plus and Minus buttons pressed
		# together then rumble and quit.
		if (buttons - cwiid.BTN_PLUS - cwiid.BTN_MINUS == 0):  
			print '\nClosing connection ...'
			wii.rumble = 1
			time.sleep(1)
			wii.rumble = 0
			wii.close()
			wiiMoteIsConnected = False
		
		# ROV Yaw control
		if (buttons & cwiid.BTN_LEFT):
			print 'ROV rotate left\n'
			ROV_rotateZ = -512
		elif(buttons & cwiid.BTN_RIGHT):
			print 'ROV rotate right\n'
			ROV_rotateZ = 512
		else:
			ROV_rotateZ = 0
	  
		# ROV Forward thrust control
		if (buttons & cwiid.BTN_B):
			print 'ROV move forward\n'
			ROV_translateX = 512
		elif(buttons & cwiid.BTN_A):
			print 'ROV move backward\n'
			ROV_translateX = -512
		else:
			ROV_translateX = 0
		
		# ROV Upward thrust control
		if (buttons & cwiid.BTN_UP):
			print 'ROV move up\n'
			ROV_translateZ = 512
		elif(buttons & cwiid.BTN_DOWN):
			print 'ROV move down\n'
			ROV_translateZ = -512
		else:
			ROV_translateZ = 0
		
		# ROV LED control
		if (buttons & cwiid.BTN_PLUS):
			if (not lightButtonDepressed):
				lightButtonDepressed = True
				LED_brightness = LED_brightness + LED_brightness_step
				print 'ROV LEDs brighter\n'
				if (LED_brightness > 512):
					LED_brightness = 512
		elif (buttons & cwiid.BTN_MINUS):
			if (not lightButtonDepressed):
				lightButtonDepressed = True
				LED_brightness = LED_brightness - LED_brightness_step
				print 'ROV LEDs dimmer\n'
				if (LED_brightness < 0):
					LED_brightness = 0
		else:
			lightButtonDepressed = False
	  
		# Video recording control
		if (buttons & cwiid.BTN_HOME):
			if ((Recording_state == 0) and (not recordButtonDepressed)):
				Recording_state = 1
				recordButtonDepressed = True
				print 'Start recording video\n'
			elif ((Recording_state == 1) and (not recordButtonDepressed)):
				Recording_state = 0
				recordButtonDepressed = True
				print 'Stopped recording video\n'
		else:
			recordButtonDepressed = False
		
		messagePacket = ("<SET_VIDEO_RECORD:{};SET_LIGHT:{};ROTATE_ROV_YAW:{}; \
							TRANSLATE_ROV_X:{};TRANSLATE_ROV_Y:0; \
							TRANSLATE_ROV_Z:{};ROTATE_CAMERA_YAW:0; \
							ROTATE_CAMERA_PITCH:0;>"
							.format(Recording_state, LED_brightness,
							ROV_rotateZ, ROV_translateX, ROV_translateZ))
	else:
		messagePacket = defaultMessagePacket
	
	print messagePacket
	
	# If the wiimote is not connected, try reconnecting it
	if (not wiiMoteIsConnected):
		try:
			wii = cwiid.Wiimote()
			print 'Wii Remote connected...\n'
			print 'Press PLUS and MINUS together to disconnect and quit.\n'
			wiiMoteIsConnected = True
			wii.rpt_mode = cwiid.RPT_BTN
			
			# Set wiimote LEDs to indicate battery level
			batteryLevel = int(100.0 * wii.state['battery'] / cwiid.BATTERY_MAX)
			if (batteryLevel > 80):
				# 4/4
				wii.led = 15
			elif (batteryLevel > 60):
				# 3/4
				wii.led = 7
			elif (batteryLevel > 40):
				# 2/4
				wii.led = 3
			elif (batteryLevel > 20):
				# 1/4
				wii.led = 1
			else:
				# 0/4
				wii.led = 0
				
		except RuntimeError:
			wiiMoteIsConnected = False
  
	# Try connecting to remote machine if conenction is lost
	if (not socketConnected):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((TCP_IP, TCP_PORT))
			socketConnected = True
		except:
			socketConnected = False
	else:
		try:
			s.send(messagePacket)
		except:
			socketConnected = False

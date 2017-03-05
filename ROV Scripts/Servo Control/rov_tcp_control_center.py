#!/usr/bin/python
#
# Receive control packets from the topside machine
# translate them into servo settings, and send over I2C
# to the servo control board
#
# Author : Eirik Taylor
# Date   : 20/02/2016
#
#	GPIO definitions:
#
#	GPIO4 - > ESC power enable
#
##############################################################

import socket
import signal
import sys
from thread import *
import recv_packet_constructor
import packet_parser
import send_control_to_servos
from subprocess import call
import time
import RPi.GPIO as GPIO

lastRecordingState = 0

############################################################################################
def treatReceviedData(inData):
	# TODO: Grab the mutex
	# Smarter TODO: Refactor so only one thread is run. Don't need to support multiple connections.
	# This would solve the unstoppable nature of the current solution also
	
	if not (inData.shutdownstate == None):
		if (inData.shutdownstate == 1):
			# Shutdown the entire system
			
			# Stop video recording first
			if (inData.videoState == 1):
				# Show live feed, but do not record to disk
				call(["/home/pi/camera/start_live_feed_noDiskStorage.sh"])
			
			# Shutdown with 'sudo shutdown -h now'
			shutdownEverything()
		
	# Send control packet to the servo controller library
	send_control_to_servos.controlServos(inData)
	
	# Control the camera recording state
	global lastRecordingState
	
	if not (inData.videoState == None):
		# Set the video recording state
		if not (inData.videoState == lastRecordingState):
			if (inData.videoState == 0):
				# Show live feed, but do not record to disk
				call(["/home/pi/camera/start_live_feed_noDiskStorage.sh"])
				print '\n\nstarting live feed\n\n'
			else:
				# Record video
				call(["/home/pi/camera/start_live_feed_withDiskStorage.sh"])
				print '\n\nstarting live feed WITH RECORDING!\n\n'
				
			lastRecordingState = inData.videoState
	
	# TODO: Release the mutex
	return

############################################################################################
def clientthread(conn):
	NewMessageStarted = False
	partialPacket = ''
	
	#Sending message to connected client
	conn.send('Welcome to the server. Receving Data...\n')

	#infinite loop so that function does not terminate and thread does not end.
	while True:
		#Receiving from client
		try:
			data = conn.recv(BUFFER_SIZE)
			if not data:
				# Socket terminated
				break
		except:
			break
		
		receivedMessagesList = recv_packet_constructor.createCompletePacket(data)
		for message in receivedMessagesList:
			receivedData = packet_parser.parseDataPacket(message)
			treatReceviedData(receivedData)
			#print receivedData

	conn.close()
	return
############################################################################################

# Capture interrupt signal (Ctrl-C). Close the TCP connection
def handler(signum, frame):
	print 'Closing socket...'
	s.close()
	GPIO.cleanup()
	sys.exit(0)

signal.signal(signal.SIGINT, handler)
############################################################################################

def shutdownEverything():
	command = "/usr/bin/sudo /sbin/shutdown -h now"
	import subprocess
	process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]
	print output
	print 'Shutting down system...\n'
	s.close()
	sys.exit(0)

##################################################################################

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)
GPIO.output(4, True)

# Set ROV to default start-up state
# Message which defaults all settings on the ROV
defaultMessagePacket = ("<SET_VIDEO_RECORD:0;SET_LIGHT:0;ROTATE_ROV_YAW:0; \
						TRANSLATE_ROV_X:0;TRANSLATE_ROV_Y:0; \
						TRANSLATE_ROV_Z:0;ROTATE_CAMERA_YAW:0; \
						ROTATE_CAMERA_PITCH:0;>")
receivedData = packet_parser.parseDataPacket(defaultMessagePacket)
treatReceviedData(receivedData)

HOST = ''   
PORT = 5005
BUFFER_SIZE = 256	# About 1.5 times the message size

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print 'Socket created'

try:
	s.bind((HOST, PORT))
except socket.error , msg:
	print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()

print 'Socket bind complete'

s.listen(2)
print 'Socket now listening'

print 'Starting video feed...'
call(["/home/pi/camera/start_live_feed_noDiskStorage.sh"])

while 1:
	#wait to accept a connection
	conn, addr = s.accept()
	print 'Connected with ' + addr[0] + ':' + str(addr[1])

	#start new thread
	start_new_thread(clientthread ,(conn,))

s.close()

#!/usr/bin/python
#
# Enable the ESCs
#
# Author : Eirik Taylor
# Date   : 20/02/2016
#
#	GPIO definitions:
#
#	GPIO4 - > ESC power enable
#
##############################################################

import sys
import time
import signal
import RPi.GPIO as GPIO

# Capture interrupt signal (Ctrl-C). Turn off ESCs
def handler(signum, frame):
	print 'Disabling ESCs...'
	GPIO.output(4, False)
	GPIO.cleanup()
	sys.exit(0)

signal.signal(signal.SIGINT, handler)

##################################################################################

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)
GPIO.output(4, True)

print 'ESCs enabled! Press Ctrl-C to disable again'

while 1:
	# Wait until user is done
	time.sleep(1000)

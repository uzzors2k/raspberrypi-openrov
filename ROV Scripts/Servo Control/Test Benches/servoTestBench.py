#!/usr/bin/python
#
# Receive control packets from the topside machine
# translate them into servo settings, and send over I2C
# to the servo control board
#
# Author : Eirik Taylor
# Date   : 08/12/2015
#

import send_control_to_servos
from packet_parser import ControlData

parsedData = ControlData(videoState=0, lightLevel=0, rovYaw=0, rovX=0, rovY=0, rovZ=0, cameraYaw=0, cameraPitch=0)

print parsedData

send_control_to_servos.controlServos(parsedData)

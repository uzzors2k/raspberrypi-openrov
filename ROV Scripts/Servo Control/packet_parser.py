#!/usr/bin/python
########################################################################
#
#	Author: Eirik Taylor, December 2015
#
########################################################################

import collections

ControlData = collections.namedtuple('ControlData', 'videoState lightLevel rovYaw rovX rovY rovZ cameraYaw cameraPitch shutdownstate')
RangeLimit = 512

#####################################################################
def parseStringNumber(token, upperLimit, lowerLimit):
	number = int(token)
	if (number > upperLimit):
		number = upperLimit
	if (number < lowerLimit):
		number = lowerLimit
	return number
	
#####################################################################
def isInt(value):
	try:
		int(value)
		return True
	except:
		return False

######################################################################
def parseDataPacket(inputData):
	# Set default values
	set_video_state = None
	set_light_state = None
	set_rov_yaw = None
	set_rov_x = None
	set_rov_y = None
	set_rov_z = None
	set_camera_yaw = None
	set_camera_pitch = None
	set_shutdown_state = None
				
	# Divide and conquer the string
	properties = inputData.split(";")
	for property in properties:
		# Match to an expected setting
		
		# Video recording
		if (parseDataPacket.video_state in property):
			# Map to a variable
			splitProperty = property.split(":")
			for token in splitProperty:
				if (isInt(token)):
					set_video_state = parseStringNumber(token, 1, 0)
					#print 'Video setting:' + str(set_video_state)
					
		# LED brightness
		elif (parseDataPacket.light_intensity in property):
			# Map to a variable
			splitProperty = property.split(":")
			for token in splitProperty:
				if (isInt(token)):
					set_light_state = parseStringNumber(token, RangeLimit, 0)
					#print 'Light setting:' + str(set_light_state)
		
		# ROV Yaw
		elif (parseDataPacket.rov_yaw in property):
			# Map to a variable
			splitProperty = property.split(":")
			for token in splitProperty:
				if (isInt(token)):
					set_rov_yaw = parseStringNumber(token, RangeLimit, -RangeLimit)
					#print 'ROV Yaw setting:' + str(set_rov_yaw)
		
		# ROV x
		elif (parseDataPacket.rov_x in property):
			# Map to a variable
			splitProperty = property.split(":")
			for token in splitProperty:
				if (isInt(token)):
					set_rov_x = parseStringNumber(token, RangeLimit, -RangeLimit)
					#print 'ROV X setting:' + str(set_rov_x)
		
		# ROV y
		elif (parseDataPacket.rov_y in property):
			# Map to a variable
			splitProperty = property.split(":")
			for token in splitProperty:
				if (isInt(token)):
					set_rov_y = parseStringNumber(token, RangeLimit, -RangeLimit)
					#print 'ROV Y setting:' + str(set_rov_y)
		
		# ROV z
		elif (parseDataPacket.rov_z in property):
			# Map to a variable
			splitProperty = property.split(":")
			for token in splitProperty:
				if (isInt(token)):
					set_rov_z = parseStringNumber(token, RangeLimit, -RangeLimit)
					#print 'ROV Z setting:' + str(set_rov_z)
		
		# ROV Camera yaw
		elif (parseDataPacket.camera_yaw in property):
			# Map to a variable
			splitProperty = property.split(":")
			for token in splitProperty:
				if (isInt(token)):
					set_camera_yaw = parseStringNumber(token, RangeLimit, -RangeLimit)
					#print 'Camera Yaw setting:' + str(set_camera_yaw)
		
		# ROV Camera pitch
		elif (parseDataPacket.camera_pitch in property):
			# Map to a variable
			splitProperty = property.split(":")
			for token in splitProperty:
				if (isInt(token)):
					set_camera_pitch = parseStringNumber(token, RangeLimit, -RangeLimit)
					#print 'Camera Pitch setting:' + str(set_camera_pitch)
		
		# System shutdown message
		elif (parseDataPacket.shutdown_state in property):
			# Map to a variable
			splitProperty = property.split(":")
			for token in splitProperty:
				if (isInt(token)):
					set_shutdown_state = parseStringNumber(token, 1, 0)
					#print 'Shutdown setting:' + str(set_shutdown_state)
		
	parsedData = ControlData(videoState=set_video_state, lightLevel=set_light_state, rovYaw=set_rov_yaw, rovX=set_rov_x, \
				rovY=set_rov_y, rovZ=set_rov_z, cameraYaw=set_camera_yaw, cameraPitch=set_camera_pitch, \
				shutdownstate=set_shutdown_state)
	
	return parsedData
	
parseDataPacket.video_state = 'SET_VIDEO_RECORD'
parseDataPacket.light_intensity = 'SET_LIGHT'
parseDataPacket.rov_yaw = 'ROTATE_ROV_YAW'
parseDataPacket.rov_x = 'TRANSLATE_ROV_X'
parseDataPacket.rov_y = 'TRANSLATE_ROV_Y'
parseDataPacket.rov_z = 'TRANSLATE_ROV_Z'
parseDataPacket.camera_yaw = 'ROTATE_CAMERA_YAW'
parseDataPacket.camera_pitch = 'ROTATE_CAMERA_PITCH'
parseDataPacket.shutdown_state = 'SYSTEM_SHUTDOWN'
########################################################################

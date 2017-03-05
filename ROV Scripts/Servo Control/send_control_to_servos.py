#!/usr/bin/python
#
# Translate a control packet into actual servo commands
# Used to control the ROV
#
# Eirik Taylor December 19th 2015
#
#################################################

from Adafruit_PWM_Servo_Driver import PWM
from PiBright_Driver import LED_PWM
from packet_parser import ControlData
from packet_parser import RangeLimit

# Define a type for all servos
class Servo:
	def __init__(self, position, reversed, minRange, maxRange):
		# Index on the servo board where this device is connected
		self.position = position
		# 0 = normal, 1 = reverse
		self.reversed = reversed
		# Min servo signal length
		self.minRange = minRange
		# Max servo signal length
		self.maxRange = maxRange

# Carefully tuned to match ESCs and servos used!
servoMin = 210  				# Min pulse length out of 4096
servoMax = 570  				# Max pulse length out of 4096

servoMinCameraPitch = 200  		# Min pulse length out of 4096
servoMaxCameraPitch = 600  		# Max pulse length out of 4096

# Fill out the correct specs for each servo
LED_DATA = Servo(0, 0, 0, 0)	# This position is only used for power
ROV_REAR_THRUSTER_RIGHT = Servo(2, 0, servoMin, servoMax)
ROV_REAR_THRUSTER_LEFT = Servo(4, 0, servoMin, servoMax)
ROV_VERTICAL_THRUSTER_RIGHT = Servo(3, 1, servoMin, servoMax)
ROV_VERTICAL_THRUSTER_LEFT = Servo(5, 1, servoMin, servoMax)
ROV_STRAFE_THRUSTER_RIGHT = Servo(6, 0, servoMin, servoMax)
ROV_STRAFE_THRUSTER_LEFT = Servo(7, 0, servoMin, servoMax)
CAMERA_PITCH = Servo(1, 0, servoMinCameraPitch, servoMaxCameraPitch)
CAMERA_YAW = Servo(8, 0, servoMinCameraPitch, servoMaxCameraPitch)

# Initialise the PWM device using the default address
pwm = PWM(0x40)
pwm.setPWMFreq(60)		# Set frequency to 60 Hz

ledPWM = LED_PWM(0x70)	# The LED board
ledPWM.initialize()

##################################################################################

def controlServos(controlPacket):

	# Mixing of forward servo channels, for steering purposes
	desiredROVYaw = 0
	desiredROVThrust = 0
	
	# Set system states
	if not (controlPacket.lightLevel == None):
		# Set the LED brightness on the servoboard PWM
		brightnessPercentage = convertToExpFloatPercentage(controlPacket.lightLevel, RangeLimit)
		setPWMchannel(LED_DATA.position, brightnessPercentage)
		# Also set this on the dedicated LED board on the camera
		ledPWM.setBrightness(brightnessPercentage)
		
	if not (controlPacket.rovYaw == None):
		# Set the ROV yaw
		desiredROVYaw = convertToFloatPercentage(controlPacket.rovYaw, RangeLimit)
		
	if not (controlPacket.rovX == None):
		# Set the ROV forward motion
		desiredROVThrust = convertToFloatPercentage(controlPacket.rovX, RangeLimit)
		
	if not (controlPacket.rovY == None):
		# Set the ROV sideways motion
		# Not used for steering currently. One is always the inverse of the other
		thrustSideways = convertToFloatPercentageCenter(controlPacket.rovY, RangeLimit)
		setServoPercentage(ROV_STRAFE_THRUSTER_RIGHT, thrustSideways)
		setServoPercentage(ROV_STRAFE_THRUSTER_LEFT, (1.0 - thrustSideways))
		
	if not (controlPacket.rovZ == None):
		# Set the ROV up/down motion
		# Both servos tied together for now
		thrustUpDownPercent = convertToFloatPercentageCenter(controlPacket.rovZ, RangeLimit)
		setServoPercentage(ROV_VERTICAL_THRUSTER_RIGHT, thrustUpDownPercent)
		setServoPercentage(ROV_VERTICAL_THRUSTER_LEFT, thrustUpDownPercent)
		
	if not (controlPacket.cameraYaw == None):
		# Set the Camera yaw
		cameraYawAmount = convertToFloatPercentageCenter(controlPacket.cameraYaw, RangeLimit)
		setServoPercentage(CAMERA_YAW, cameraYawAmount)
		
	if not (controlPacket.cameraPitch == None):
		# Set the Camera pitch
		cameraPitchAmount = convertToFloatPercentageCenter(controlPacket.cameraPitch, RangeLimit)
		setServoPercentage(CAMERA_PITCH, cameraPitchAmount)
	
	# REFACTOR: Changing left/right inversion was just a matter of reversing one signal
	#			Also strange motor behaviour when going forward and turning at the same time
	
	# Determine thrust in [1, -1] space
	MotorRightThrust = -desiredROVYaw
	MotorLeftThrust = desiredROVYaw
	MotorRightThrust = MotorRightThrust + desiredROVThrust
	MotorLeftThrust = MotorLeftThrust + desiredROVThrust
	if (MotorRightThrust > 1.0):
		MotorRightThrust = 1.0
	elif (MotorRightThrust < -1.0):
		MotorRightThrust = -1.0
	if (MotorLeftThrust > 1.0):
		MotorLeftThrust = 1.0
	elif (MotorLeftThrust < -1.0):
		MotorLeftThrust = -1.0
	
	# Map to [0, 1] space
	MotorRightThrust = MotorRightThrust + 1.0
	MotorLeftThrust = MotorLeftThrust + 1.0
	MotorRightThrust = MotorRightThrust / 2.0
	MotorLeftThrust = MotorLeftThrust / 2.0
	
	# Set forward motion
	setServoPercentage(ROV_REAR_THRUSTER_RIGHT, MotorRightThrust)
	setServoPercentage(ROV_REAR_THRUSTER_LEFT, MotorLeftThrust)
	
	return

##################################################################################

def setServoPercentage(servoData, percentage):
	# Limit the input
	if (percentage > 1.0):
		percentage = 1.0
	elif (percentage < 0.0):
		percentage = 0.0
	
	# Reverse the direction if required
	if (servoData.reversed == 1):
		percentage = 1.0 - percentage
	
	# Set the PWM output
	pulse = percentage * (servoData.maxRange - servoData.minRange)
	pulse = pulse + servoData.minRange
	pwm.setPWM(int(servoData.position), 0, int(pulse))
	return int(pulse)
	
##################################################################################

def setPWMchannel(channel, percentage):

	# Limit the input
	if (percentage > 1.0):
		percentage = 1.0
	elif (percentage < 0.0):
		percentage = 0.0
		
	# Set the PWM output
	pulse = percentage * 4095
	pwm.setPWM(int(channel), 0, int(pulse))
	return
	
##################################################################################

def convertToFloatPercentageCenter(input, limit):
	# Convert an input to a float between 0.0 and 1.0
	return float((limit + input)) / float((2 * limit))
	
##################################################################################

def convertToFloatPercentage(input, limit):
	# Convert an input to a float between -1.0 and 1.0
	return float(input) / float(limit)
	
##################################################################################

def convertToExpFloatPercentage(input, limit):
	percentage = convertToFloatPercentage(input, limit)
	return percentage * percentage
	
##################################################################################
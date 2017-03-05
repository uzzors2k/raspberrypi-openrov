#!/usr/bin/python

from Adafruit_I2C import Adafruit_I2C

# ============================================================================
# PiBright Driver (Semtech SC620 I2C LED driver)
# ============================================================================

class LED_PWM :
	# Registers/etc.
	__LED_CONTROL        = 0x00
	__GAIN               = 0x09
	__CENTER1            = 0x01
	__CENTER2            = 0x03
	__CENTER3            = 0x06
	__CENTER4            = 0x08
	__CORNER1            = 0x02
	__CORNER2            = 0x04
	__CORNER3            = 0x05
	__CORNER4            = 0x07

	# Bit Masks
	__CORNERLEDS         = 0x5A
	__CENTERLEDS         = 0xA5
	__FULLON             = 0xFF
	__FULLOFF            = 0x00
	__MAXGAIN            = 0x0F
	__MAXBRIGHTNESS      = 0x32

	general_call_i2c = Adafruit_I2C(0x00)

	def __init__(self, address=0x70):
		self.i2c = Adafruit_I2C(address)
		self.address = address
		self.i2c.write8(self.__LED_CONTROL, self.__FULLOFF)

	def initialize(self):
		self.i2c.write8(self.__LED_CONTROL, self.__FULLON)
		self.i2c.write8(self.__GAIN, self.__MAXGAIN)

	def allLEDsOff(self):
		self.i2c.write8(self.__LED_CONTROL, self.__FULLOFF)

	def setBrightness(self, percent):
		pwmValue = self.__MAXBRIGHTNESS * percent
		self.i2c.write8(self.__CENTER1, int(pwmValue))
		self.i2c.write8(self.__CENTER2, int(pwmValue))
		self.i2c.write8(self.__CENTER3, int(pwmValue))
		self.i2c.write8(self.__CENTER4, int(pwmValue))
		self.i2c.write8(self.__CORNER1, int(pwmValue))
		self.i2c.write8(self.__CORNER2, int(pwmValue))
		self.i2c.write8(self.__CORNER3, int(pwmValue))
		self.i2c.write8(self.__CORNER4, int(pwmValue))

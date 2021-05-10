#!/usr/bin/python3

import smbus
import time
from math import *

bus = smbus.SMBus(1);            # 0 for R-Pi Rev. 1, 1 for Rev. 2

# General constants
EARTH_GRAVITY_MS2    = 9.80665 # m/s2

# the following address is defined by datasheet
#HMC5883L (Magnetometer) constants
HMC5883L_ADDRESS        =    0x1E  # I2C address
    
HMC5883L_CRA            =    0x00  # write CRA(00), Configuration Register A
HMC5883L_CRB            =    0x01  # write CRB(01), Configuration Register B
HMC5883L_MR             =    0x02  # write Mode(02)
HMC5883L_DO_X_H         =    0x03  # Data Output
HMC5883L_DO_X_L         =    0x04
HMC5883L_DO_Z_H         =    0x05
HMC5883L_DO_Z_L         =    0x06
HMC5883L_DO_Y_H         =    0x07
HMC5883L_DO_Y_L         =    0x08


# the following address is defined by datasheet
ADXL345_ADDRESS         =    0x53 # I2C address

ADXL345_BW_RATE         =    0x2C # Data rate and power mode control 
ADXL345_POWER_CTL       =    0x2D # Power-saving features control 
ADXL345_DATA_FORMAT     =    0x31 # Data format control 
ADXL345_DATAX0          =    0x32
ADXL345_DATAX1          =    0x33
ADXL345_DATAY0          =    0x34
ADXL345_DATAY1          =    0x35
ADXL345_DATAZ0          =    0x36
ADXL345_DATAZ1          =    0x37
# ---------------------------------

# set value
ADXL345_SCALE_MULTIPLIER= 0.00390625    # G/LSP. 1/256 = 0.00390625
ADXL345_BW_RATE_100HZ   = 0x0A          # 0A = 0000 1111
ADXL345_MEASURE         = 0x08          # 08 = 0000 1000



class IMU(object):

    def write_byte(self,adr, value):
        bus.write_byte_data(self.ADDRESS, adr, value)
    
    def read_byte(self,adr):
        return bus.read_byte_data(self.ADDRESS, adr)

    def read_word(self,adr,rf=1):
        # rf=1 Little Endian Format, rf=0 Big Endian Format
        if (rf == 1):
            # acc, gyro 
            low = self.read_byte(adr)
            high = self.read_byte(adr+1)
        else:
            # compass
            high = self.read_byte(adr)
            low = self.read_byte(adr+1)
        val = (high << 8) + low
        return val

    def read_word_2c(self,adr,rf=1):
        val = self.read_word(adr,rf)
        if(val & (1 << 16 - 1)):
            return val - (1<<16)
        else:
            return val

class gy801(object):
    def __init__(self) :
        self.compass = HMC5883L()
        self.accel = ADXL345()



# -----------------------------------------------------
class ADXL345(IMU):
    
    ADDRESS = ADXL345_ADDRESS

    def __init__(self) :
        #Class Properties
        self.Xoffset = 0.0  # unit: G, modify by yourself
        self.Yoffset = 0.0  # unit: G, modify by yourself
        self.Zoffset = 0.0  # unit: G, modify by yourself
        self.Xraw = 0.0
        self.Yraw = 0.0
        self.Zraw = 0.0
        self.Xg = 0.0
        self.Yg = 0.0
        self.Zg = 0.0
        self.X = 0.0
        self.Y = 0.0
        self.Z = 0.0
        self.t0x = None
        self.t0y = None
        self.t0z = None

        self.df_value = 0b00001000 
        
        self.Xcalibr = ADXL345_SCALE_MULTIPLIER
        self.Ycalibr = ADXL345_SCALE_MULTIPLIER
        self.Zcalibr = ADXL345_SCALE_MULTIPLIER

        # Register 0x2C: BW_RATE
        self.write_byte(ADXL345_BW_RATE, ADXL345_BW_RATE_100HZ)    
        # write value= 0x0A = 00001111
        # D3-D0: The default value is 0x0A, 
        # which translates to a 100 Hz output data rate.


        # Register 0x2D: POWER_CTL 
        self.write_byte(ADXL345_POWER_CTL, ADXL345_MEASURE)    
        # write value: 0x08 = 00001000
        # D3=1: set 1 for measurement mode.


        # Register 0x31: DATA_FORMAT 
        self.write_byte(ADXL345_DATA_FORMAT, self.df_value)
        # write value=00001000
        # D3 = 1: the device is in full resolution mode, 
        # where the output resolution increases with the g range 
        # set by the range bits to maintain a 4 mg/LSB scale factor. 
        # D1 D0 = range. 00 = +-2g 

    
    # RAW readings in LPS
    # Register 0x32 to Register 0x37:
    # DATAX0, DATAX1, DATAY0, DATAY1, DATAZ0, DATAZ1 (Read Only)
    def getRawX(self) :
        self.Xraw = self.read_word_2c(ADXL345_DATAX0)
        return self.Xraw

    def getRawY(self) :
        self.Yraw = self.read_word_2c(ADXL345_DATAY0)
        return self.Yraw
    
    def getRawZ(self) :
        self.Zraw = self.read_word_2c(ADXL345_DATAZ0)
        return self.Zraw

    # G related readings in g
    # similar to filter. combine current value with previous one.
    # plf = 1 means it only uses "current reading"
    def getXg(self,plf = 1.0) :
        self.Xg = (self.getRawX() * self.Xcalibr - self.Xoffset) * plf + (1.0 - plf) * self.Xg
        return self.Xg

    def getYg(self,plf = 1.0) :
        self.Yg = (self.getRawY() * self.Ycalibr - self.Yoffset) * plf + (1.0 - plf) * self.Yg
        return self.Yg

    def getZg(self,plf = 1.0) :
        self.Zg = (self.getRawZ() * self.Zcalibr - self.Zoffset) * plf + (1.0 - plf) * self.Zg
        return self.Zg
    
    # Absolute reading in m/s2
    def getX(self,plf = 1.0) :
        self.X = self.getXg(plf) * EARTH_GRAVITY_MS2
        return self.X
    
    def getY(self,plf = 1.0) :
        self.Y = self.getYg(plf) * EARTH_GRAVITY_MS2
        return self.Y
    
    def getZ(self,plf = 1.0) :
        self.Z = self.getZg(plf) * EARTH_GRAVITY_MS2
        return self.Z


# -----------------------------------------------------

class HMC5883L(IMU):
    
    ADDRESS = HMC5883L_ADDRESS

    def __init__(self) :
        #Class Properties
        self.X = None
        self.Y = None
        self.Z = None
        self.angle = None
        self.Xoffset = 211
        self.Yoffset = -87
        self.Zoffset = -590
        
        # Declination Angle
        self.angle_offset = ( -1 * (4 + (32/60))) / (180 / pi)
        # Formula: (deg + (min / 60.0)) / (180 / M_PI);
        # ex: Hsinchu = Magnetic Declination: -4 deg, 32 min
        # declinationAngle = ( -1 * (4 + (32/60))) / (180 / pi)
        # http://www.magnetic-declination.com/
        
        self.scale = 0.92 # convert bit value(LSB) to gauss. DigitalResolution

        # Configuration Register A
        self.write_byte(HMC5883L_CRA, 0b01110000)

        # Configuration Register B
        self.write_byte(HMC5883L_CRB, 0b00100000)
        
        # Mode Register
        self.write_byte(HMC5883L_MR, 0b00000000)

    def getX(self):
        self.X = (self.read_word_2c(HMC5883L_DO_X_H, rf=0) - self.Xoffset) * self.scale
        return self.X

    def getY(self):
        self.Y = (self.read_word_2c(HMC5883L_DO_Y_H, rf=0) - self.Yoffset) * self.scale
        return self.Y

    def getZ(self):
        self.Z = (self.read_word_2c(HMC5883L_DO_Z_H, rf=0) - self.Zoffset) * self.scale
        return self.Z
    
    def getHeading(self):
        bearing  = degrees(atan2(self.getY(), self.getX()))

        if (bearing < 0):
            bearing += 360
        if (bearing > 360):
            bearing -= 360
        self.angle = bearing + self.angle_offset
        return self.angle



try:
    sensors = gy801()
    compass = sensors.compass
    adxl345 = sensors.accel

    while True:
        magx = compass.getX()
        magy = compass.getY()
        magz = compass.getZ()
    
        # --------------------------------------------------
        # calculate pitch, roll, tilt
        aX = adxl345.getX()
        aY = adxl345.getY()
        aZ = adxl345.getZ()
        
        roll = atan2(aY,aZ) 
        pitch = -1 * atan2(-aX,sqrt(aY*aY+aZ*aZ)) 
        # --------------------------------------------------
        
        
        # --------------------------------------------------
        # Heading
        bearing1  = degrees(atan2(magy, magx))

        if (bearing1 < 0):
            bearing1 += 360
        if (bearing1 > 360):
            bearing1 -= 360
        bearing1 = bearing1 + compass.angle_offset
        
        # Tilt compensate
        compx = magx * cos(pitch) + magz * sin(pitch)
        compy = magx * sin(roll) * sin(pitch) \
                + magy * cos(roll) \
                - magz * sin(roll) * cos(pitch)

        bearing2  = degrees(atan2(compy, compx))
        if (bearing2 < 0):
            bearing2 += 360
        if (bearing2 > 360):
            bearing2 -= 360
        bearing2 = bearing2 + compass.angle_offset
        # --------------------------------------------------

        
        print ("Compass: " )
        print ("X = %d ," % ( magx )),
        print ("Y = %d ," % ( magy )),
        print ("Z = %d (gauss)" % ( magz ))
        print ("tiltX = %.3f ," % ( compx )),
        print ("tiltY = %.3f ," % ( compy )),
      
        print ("Angle offset = %.3f deg" % ( compass.angle_offset ))
        print ("Original Heading = %.3f deg, " % ( bearing1 )), 
        print ("Tilt Heading = %.3f deg, " % ( bearing2 ))
        time.sleep(1)

        
except KeyboardInterrupt:
    print("Cleanup")

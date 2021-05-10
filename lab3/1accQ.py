import smbus
import time
from math import *

bus = smbus.SMBus(1);            # 0 for R-Pi Rev. 1, 1 for Rev. 2

EARTH_GRAVITY_MS2    = 9.80665 # m/s2

ADXL345_ADDRESS    =    0x53

ADXL345_BW_RATE          =    0x2C 
ADXL345_POWER_CTL        =    0x2D 
ADXL345_DATA_FORMAT      =    0x31 
ADXL345_DATAX0           =    0x32
ADXL345_DATAY0           =    0x34
ADXL345_DATAZ0           =    0x36
ADXL345_SCALE_MULTIPLIER = 0.00390625    # G/LSP
ADXL345_BW_RATE_100HZ    = 0x0A
ADXL345_MEASURE          = 0x08

class IMU(object):

    def write_byte(self,adr, value):
        bus.write_byte_data(self.ADDRESS, adr, value)
    
    def read_byte(self,adr):
        return bus.read_byte_data(self.ADDRESS, adr)

    def read_word(self,adr,rf=1):
        # rf=1 Little Endian Format, rf=0 Big Endian Format
        if (rf == 1):
            low = self.read_byte(adr)
            high = self.read_byte(adr+1)
        else:
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
        self.accel = ADXL345()

class ADXL345(IMU):
    
    ADDRESS = ADXL345_ADDRESS
    
    def __init__(self) :
        #Class Properties
        self.Xoffset = 0.15
        self.Yoffset = 0.023
        self.Zoffset = -0.075
        self.Yraw = 0.0
        self.Zraw = 0.0
        self.Xg = 0.0
        self.Yg = 0.0
        self.Zg = 0.0
        self.X = 0.0
        self.Y = 0.0
        self.Z = 0.0
        self.df_value = 0b00001000    # Self test disabled, 4-wire interface
                                # Full resolution, Range = +/-2g
        self.Xcalibr = ADXL345_SCALE_MULTIPLIER
        self.Ycalibr = ADXL345_SCALE_MULTIPLIER
        self.Zcalibr = ADXL345_SCALE_MULTIPLIER

        self.write_byte(ADXL345_BW_RATE, ADXL345_BW_RATE_100HZ)    # Normal mode, Output data rate = 100 Hz
        self.write_byte(ADXL345_POWER_CTL, ADXL345_MEASURE)    # Auto Sleep disable
        self.write_byte(ADXL345_DATA_FORMAT, self.df_value)    
    
    # RAW readings in LPS
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
    def getXg(self,plf = 1.0) :
        self.Xg = (self.getRawX() * self.Xcalibr + self.Xoffset) * plf + (1.0 - plf) * self.Xg
        return self.Xg

    def getYg(self,plf = 1.0) :
        self.Yg = (self.getRawY() * self.Ycalibr + self.Yoffset) * plf + (1.0 - plf) * self.Yg
        return self.Yg

    def getZg(self,plf = 1.0) :
        self.Zg = (self.getRawZ() * self.Zcalibr + self.Zoffset) * plf + (1.0 - plf) * self.Zg
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

    # write your code
    def getPitch(self) :
        aX = self.getXg()
        aY = self.getYg()
        aZ = self.getZg()
        self.pitch = atan2(-aX, sqrt(aY ** 2 + aZ ** 2))#radius
        self.pitch = degrees(self.pitch)
        return self.pitch 

    def getRoll(self) :
        aX = self.getXg()
        aY = self.getYg()
        aZ = self.getZg()
        self.roll = atan2(aY, aZ) #radius
        self.roll = degrees(self.roll)
        return self.roll


try:
    sensors = gy801()
    adxl345 = sensors.accel
    
    while True:

        adxl345.getX()
        adxl345.getY()
        adxl345.getZ()

        print ("ACC: ")
        print ("x = %.3f m/s2" % ( adxl345.X ))
        print ("y = %.3f m/s2" % ( adxl345.Y ))
        print ("z = %.3f m/s2" % ( adxl345.Z ))
        #print ("x = %.3fG" % ( adxl345.Xg ))
        #print ("y = %.3fG" % ( adxl345.Yg ))
        #print ("z = %.3fG" % ( adxl345.Zg ))
        #print ("x = %.3f" % ( adxl345.Xraw ))
        #print ("y = %.3f" % ( adxl345.Yraw ))
        #print ("z = %.3f" % ( adxl345.Zraw ))
        a = sqrt(adxl345.X ** 2 + adxl345.Y ** 2 + adxl345.Z ** 2)
        print ("a norm = %.3f m/s2" % ( a ))
        print ("pitch = %.3f in degree" % ( adxl345.getPitch() ))
        print ("roll = %.3f in degree" % ( adxl345.getRoll() ))
        time.sleep(1)
        
except KeyboardInterrupt:
    print("Cleanup")

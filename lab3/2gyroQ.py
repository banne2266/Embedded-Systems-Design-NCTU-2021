import smbus
import time
from math import *

bus = smbus.SMBus(1);            # 0 for R-Pi Rev. 1, 1 for Rev. 2

L3G4200D_ADDRESS        =    0x69
L3G4200D_CTRL_REG1      =    0x20
L3G4200D_CTRL_REG4      =    0x23
L3G4200D_OUT_X_L        =    0x28
L3G4200D_OUT_X_H        =    0x29
L3G4200D_OUT_Y_L        =    0x2A
L3G4200D_OUT_Y_H        =    0x2B
L3G4200D_OUT_Z_L        =    0x2C
L3G4200D_OUT_Z_H        =    0x2D

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
        self.gyro = L3G4200D()
        self.accel = ADXL345()


class L3G4200D(IMU):
    
    ADDRESS = L3G4200D_ADDRESS

    def __init__(self) :
        #Class Properties
        self.Xraw = 0.0
        self.Yraw = 0.0
        self.Zraw = 0.0
        self.X = 0.0
        self.Y = 0.0
        self.Z = 0.0
        self.Xangle = 0.0
        self.Yangle = 0.0
        self.Zangle = 0.0
        self.t0x = None
        self.t0y = None
        self.t0z = None
        
        self.pitch = 0
        self.roll = 0

        # set value
        self.gain_std = 0.00875    # dps/digit
        
        self.write_byte(L3G4200D_CTRL_REG1, 0x0F)
        self.write_byte(L3G4200D_CTRL_REG4, 0x80)

        self.setCalibration()

    def setCalibration(self) :
        gyr_r = self.read_byte(L3G4200D_CTRL_REG4)
        
        self.gain = 2 ** ( gyr_r & 48 >> 4) * self.gain_std

    def getRawX(self):
        self.Xraw = self.read_word_2c(L3G4200D_OUT_X_L)
        return self.Xraw

    def getRawY(self):
        self.Yraw = self.read_word_2c(L3G4200D_OUT_Y_L)
        return self.Yraw

    def getRawZ(self):
        self.Zraw = self.read_word_2c(L3G4200D_OUT_Z_L)
        return self.Zraw

    def getX(self,plf = 1.0):
        self.X = ( self.getRawX() * self.gain ) * plf + (1.0 - plf) * self.X
        return self.X

    def getY(self,plf = 1.0):
        self.Y = ( self.getRawY() * self.gain ) * plf + (1.0 - plf) * self.Y
        return self.Y

    def getZ(self,plf = 1.0):
        self.Z = ( self.getRawZ() * self.gain ) * plf + (1.0 - plf) * self.Z
        return self.Z
    
    def getXangle(self,plf = 1.0) :
        if self.t0x is None : self.t0x = time.time()
        t1x = time.time()
        LP = t1x - self.t0x
        self.t0x = t1x
        self.Xangle = self.getX(plf) * LP
        self.Xangle = degrees(self.Xangle)
        return self.Xangle
    
    def getYangle(self,plf = 1.0) :
        if self.t0y is None : self.t0y = time.time()
        t1y = time.time()
        LP = t1y - self.t0y
        self.t0y = t1y
        self.Yangle = self.getY(plf) * LP
        self.Yangle = degrees(self.Yangle)
        return self.Yangle
    
    def getZangle(self,plf = 1.0) :
        if self.t0z is None : self.t0z = time.time()
        t1z = time.time()
        LP = t1z - self.t0z
        self.t0z = t1z
        self.Zangle = self.getZ(plf) * LP
        self.Zangle = degrees(self.Zangle)
        return self.Zangle
       
    def getPitch(self, accp) :
        self.pitch = (self.pitch + self.Xangle) * 0.98 + accp * 0.02
        return self.pitch 

    def getRoll(self, accr) :
        self.roll = (self.roll + self.Yangle) * 0.98 + accr * 0.02
        return self.roll


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
    # if run directly we'll just create an instance of the class and output 
    # the current readings
    
    sensors = gy801()
    adxl345 = sensors.accel
    gyro = sensors.gyro
    
    while True:
        gyro.getXangle()
        gyro.getYangle()
        gyro.getZangle()

        print ("Gyro: ")
        print ("Xangle = %.3f deg" % ( gyro.getXangle() ))
        print ("Yangle = %.3f deg" % ( gyro.getYangle() ))
        print ("Zangle = %.3f deg" % ( gyro.getZangle() ))
        
        print ("pitch = %.3f in degree" % ( gyro.getPitch(adxl345.getPitch()) ))
        print ("roll = %.3f in degree" % ( gyro.getRoll(adxl345.getRoll()) ))
        
        time.sleep(1)
        
except KeyboardInterrupt:
    print("Cleanup")

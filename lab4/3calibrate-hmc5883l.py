#!/usr/bin/env python
import smbus
import time
import math

#Local import: i2cutils.py
from i2cutils import i2c_raspberry_pi_bus_number

bus = smbus.SMBus(1)
address = 0x1e

def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def write_byte(adr, value):
    bus.write_byte_data(address, adr, value)

write_byte(0, 0b01110000) # Set to 8 samples @ 15Hz
write_byte(1, 0b00100000) # 1.3 gain LSb / Gauss 1090 (default)
write_byte(2, 0b00000000) # Continuous sampling

minx = 0
maxx = 0
miny = 0
maxy = 0
minz = 0
maxz = 0

print "Now repeatedly rotate the hmc5883l around all three axes"

for i in range(0,100):
    x_out = read_word_2c(3)
    y_out = read_word_2c(7)
    z_out = read_word_2c(5)
    
    
    if x_out < minx:
        minx=x_out
    
    if y_out < miny:
        miny=y_out

    if z_out < minz:
        minz=z_out
    
    if x_out > maxx:
        maxx=x_out
    
    if y_out > maxy:
        maxy=y_out

    if z_out > maxz:
        maxz=z_out
   
    print ("x: %.0f - %.0f, y: %.0f - %.0f, z: %.0f - %.0f" % (minx, maxx, miny, maxy, minz, maxz) )
    
    time.sleep(0.1)

print "results:"
print ( "x: min, max = %.0f, %.0f" % (minx, maxx) )
print ( "y: min, max = %.0f, %.0f" % (miny, maxy) )
print ( "z: min, max = %.0f, %.0f" % (minz, maxz) )

print "x offset: ", (maxx + minx) / 2
print "y offset: ", (maxy + miny) / 2
print "z offset: ", (maxz + minz) / 2

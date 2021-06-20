import cv2
import numpy as np
import RPi.GPIO as GPIO
import os
import Car
import sg90
import time
import HandTrackingModule as htm
import whiskey

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(detectionCon=0.75)
tipIds = [4, 8, 12, 16, 20] # tips of five fingers

car = Car.Car(19,26,6,13)
water_pump = whiskey.whiskey(20)
whiskey_pump = whiskey.whiskey(21)
peanut = sg90.sg90(12)
whiskey_cnt = 0
cooldown = 0
state = 0

try:
    while True:
        sccuess, img = cap.read()
        if not sccuess:
            print("camera fail")
            cv2.waitKey(33)
            continue
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw = False)
        if len(lmList)!=0 and state == 1:
            fingers = []

            if lmList[4][1] < lmList[3][1]: # thumb
                fingers.append(0)
            else:
                fingers.append(1)

            for id in range(1,5): # except for the thumb finger
                if lmList[tipIds[id]][2] < lmList[tipIds[id]-2][2]: # open hand : check if the finger dot is lower then the low joint
                    fingers.append(1)
                else:
                    fingers.append(0)

            
            totalFingers = fingers.count(1) # how many finger is opened
            print(fingers, totalFingers)
            
            if totalFingers == 1 and cooldown == 0:
                os.system('omxplayer -o alsa 2.mp3')
                water_pump.start()
                time.sleep(1)
                water_pump.stop()
                os.system('omxplayer -o alsa bridge.mp3')
                cooldown = 30
            elif totalFingers == 2 and cooldown == 0:
                os.system('omxplayer -o alsa 1.mp3')
                whiskey_pump.start()
                time.sleep(1)
                whiskey_pump.stop()
                whiskey_cnt = min(whiskey_cnt + 1, 9)
                os.system('omxplayer -o alsa bridge.mp3')
                cooldown = 30
            elif totalFingers == 3 and cooldown == 0:
                os.system('omxplayer -o alsa 4-1.mp3')
                os.system('omxplayer -o alsa 0' + str(whiskey_cnt) + '.mp3')
                os.system('omxplayer -o alsa 4-3.mp3')
                os.system('omxplayer -o alsa bridge.mp3')
                cooldown = 30
            elif totalFingers == 4 and cooldown == 0:
                os.system('omxplayer -o alsa 4.mp3')
                for i in range(30):
                    peanut.change_dutycycle(12)
                    time.sleep(0.25)
                    peanut.change_dutycycle(2)
                    time.sleep(0.25)
                cooldown = 30
                os.system('omxplayer -o alsa bridge.mp3')
            elif totalFingers == 5 and cooldown == 0:
                os.system('omxplayer -o alsa 5.mp3')
                os.system('omxplayer -o alsa bridge.mp3')
                cooldown = 30
                state = 0
        if sccuess:
            cv2.imshow("look", img)
        key = cv2.waitKey(33)
        if key != -1:
            car.control(key)
        if key == ord('x') and state == 0:
            os.system('omxplayer -o alsa start.mp3')
            state = 1
            cooldown = 30
        cooldown = max(cooldown - 1, 0)
except KeyboardInterrupt:
    print("KeyboardInterrupt")
finally:
    GPIO.cleanup()
    
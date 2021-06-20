import cv2
import time
import os
import HandTrackingModule as htm

#3:44:18
wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

folderPath = "./FingerImages/"
myList = os.listdir(folderPath)
print(myList)
overlayList = []
for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    #print(f'{folderPath}/{imPath}')
    overlayList.append(image)

#print(len(overlayList))
pTime = 0

detector = htm.handDetector(detectionCon=0.75)
tipIds = [4, 8, 12, 16, 20] # tips of five fingers
while True:
    sccuess, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw = False)
    #print(lmList)
    if len(lmList)!=0:
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

        #print(fingers)
        totalFingers = fingers.count(1) # how many finger is opened
        # if totalFingers == 0:
        # elif totalFingers == 1:
        # elif totalFingers == 2:
        # elif totalFingers == 3:   
        # elif totalFingers == 4:
        # elif totalFingers == 5:
             
        tmp = overlayList[totalFingers]
        tmp_resized = cv2.resize(tmp,(200,200))
        h, w, c = tmp_resized.shape
        img[0:h, 0:w] = tmp_resized  # show the relative picture
    
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, f'FPS:{int(fps)}', (400, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)


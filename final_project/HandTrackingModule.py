import cv2
import mediapipe as mp  # by google
import time

# ctrl+/ : fast comments
# shft+alt+a： fast mult-line comments

class handDetector():
    def __init__(self, mode=False, maxHands = 2, detectionCon = 0.5, trackCon = 0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True): # little red dot (by tracking)
        imgRGB = cv2.cvtColor( img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        #print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks: # it could be multiple hands
            for handLms in self.results.multi_hand_landmarks:
                if draw == True:
                    self.mpDraw.draw_landmarks( img, handLms, self.mpHands.HAND_CONNECTIONS)  # draw landmarks(dots) in the hands
        return img

    def findPosition(self, img, handNo=0, draw=True): # big pink dots (by drawing)

        lmList = []
        if self.results.multi_hand_landmarks: # it could be multiple hands
            myHand = self.results.multi_hand_landmarks[handNo]

            for id, lm in enumerate(myHand.landmark):
                #print(id,lm)
                h, w, c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                #print( id, cx, cy)
                lmList.append([id, cx,cy])

                if draw: # hand-root  # 4: first finger top
                    cv2.circle( img, (cx,cy), 10, (34,10,99), cv2.FILLED)
        return lmList

def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition( img)
        if len(lmList) != 0:
            print(lmList[4]) # print theposition of the dot of finger 

        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime

        cv2.putText( img, str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3) # img, words, position, fonts, fonts_size (scale), color, thikness
        
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
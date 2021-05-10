# import the necessary packages
from __future__ import print_function
from imutils.video import FPS

import imutils
import time
import cv2

try:
    # grab a pointer to the video stream 
    # and initialize the FPS counter
    print("[INFO] sampling frames from webcam...")
    vs = cv2.VideoCapture(0)
    time.sleep(2.0)
    text = str(0)

    # loop over some frames
    while True:
        fps = FPS().start()
        for i in range(10):
        
            # grab the frame from the stream and resize it to have a maximum
            # width of 400 pixels
            (grabbed, frame) = vs.read()
            frame = imutils.resize(frame, width=400)
            frame = cv2.putText(frame, text, (20,200), cv2.FONT_HERSHEY_PLAIN, 10, (255,0,0))

            # update the FPS counter
            fps.update()

            # Display image
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break # press q to quit without calculating
        fps.stop()
        text = str(fps.fps())
        
except KeyboardInterrupt:
    # Use ctrl + c to stop the timer and display FPS information
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    # do a bit of cleanup
    vs.release()
    cv2.destroyAllWindows()
    
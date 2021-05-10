# import the necessary packages
from __future__ import print_function
from imutils.video import WebcamVideoStream
from imutils.video import FPS

import imutils
import time
import cv2

try:
    # created a *threaded *video stream, allow the camera sensor to warmup,
    # and start the FPS counter
    print("[INFO] sampling frames from WebcamVideoStream module...")
    vs = WebcamVideoStream(src=0).start()
    time.sleep(2.0)
    fps = FPS().start()
    text = str(0)

    # loop over some frames
    while True:
        fps = FPS().start()
        for i in range(10):
        
            # grab the frame from the stream and resize it to have a maximum
            # width of 400 pixels
            frame = vs.read()
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
    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()
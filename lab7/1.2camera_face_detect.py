import sys
import cv2

cascPath = "model/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)

if cv2.__version__.startswith('2'):
    PROP_FRAME_WIDTH = cv2.cv.CV_CAP_PROP_FRAME_WIDTH
    PROP_FRAME_HEIGHT = cv2.cv.CV_CAP_PROP_FRAME_HEIGHT
elif cv2.__version__.startswith('3'):
    PROP_FRAME_WIDTH = cv2.CAP_PROP_FRAME_WIDTH
    PROP_FRAME_HEIGHT = cv2.CAP_PROP_FRAME_HEIGHT

# video source
vs = cv2.VideoCapture(0)
vs.set(PROP_FRAME_WIDTH, 320)
vs.set(PROP_FRAME_HEIGHT, 240)

while True:
    # Capture frame-by-frame
    ret, frame = vs.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # https://docs.opencv.org/2.4/modules/objdetect/doc/cascade_classification.html
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    print ("Found {0} faces!".format(len(faces)))

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow("preview", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# When everything is done, release the capture
vs.release()
cv2.destroyAllWindows()

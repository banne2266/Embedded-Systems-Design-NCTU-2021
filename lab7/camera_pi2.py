#!/usr/bin/python
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#|R|a|s|p|b|e|r|r|y|P|i|.|c|o|m|.|t|w|
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# Copyright (c) 2014, raspberrypi.com.tw
# All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Author : sosorry
# Date   : 05/31/2015
# Origin : http://blog.miguelgrinberg.com/post/video-streaming-with-flask
from imutils import face_utils
from imutils.video.pivideostream import PiVideoStream
import numpy as np
import imutils
import dlib
import cv2
import sys
import time

class Camera(object):
    def __init__(self):
        if cv2.__version__.startswith('2'):
            PROP_FRAME_WIDTH = cv2.cv.CV_CAP_PROP_FRAME_WIDTH
            PROP_FRAME_HEIGHT = cv2.cv.CV_CAP_PROP_FRAME_HEIGHT
        elif cv2.__version__.startswith('3'):
            PROP_FRAME_WIDTH = cv2.CAP_PROP_FRAME_WIDTH
            PROP_FRAME_HEIGHT = cv2.CAP_PROP_FRAME_HEIGHT
        

        self.video = PiVideoStream().start()
        time.sleep(4)
        #self.video = cv2.VideoCapture(1)
        #self.video.set(PROP_FRAME_WIDTH, 640)
        #self.video.set(PROP_FRAME_HEIGHT, 480)
        #self.video.set(PROP_FRAME_WIDTH, 320)
        #self.video.set(PROP_FRAME_HEIGHT, 240)
        
        self.detector = dlib.get_frontal_face_detector()

        self.predictor_file = "model/shape_predictor_68_face_landmarks.dat"
        self.predictor = dlib.shape_predictor(self.predictor_file)
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        image = self.video.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        rects = self.detector(gray, 1)
        for (i, rect) in enumerate(rects):
            # determine the facial landmarks for the face region, then
            # convert the facial landmark (x, y)-coordinates to a NumPy
            # array
            shape = self.predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            # convert dlib's rectangle to a OpenCV-style bounding box
            # [i.e., (x, y, w, h)], then draw the face bounding box
            (x, y, w, h) = face_utils.rect_to_bb(rect)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # show the face number
            cv2.putText(image, "Face #{}".format(i + 1), (x - 10, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # loop over the (x, y)-coordinates for the facial landmarks
            # and draw them on the image
            for (x, y) in shape:
                cv2.circle(image, (x, y), 1, (0, 0, 255), -1)
        
        
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tostring()

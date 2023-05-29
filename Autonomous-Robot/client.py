#!/usr/bin/env python3

import cv2
from time import sleep, time
import struct
import redis
import numpy as np
import os
import pickle

def fromRedis(r,n):
   imdata = r.hgetall(n)                                               # get image dictionary from the server 
   encoded = imdata[b'image']
   fnum = imdata[b'frame']
   h, w = struct.unpack('>II',encoded[:8])                             # the first 8 bytes are h,w to use in the reshape
   a = np.frombuffer(encoded, dtype=np.uint8, offset=8).reshape(h,w,3) # start at offset 8, create
                                                                       # 1-dimensional array with the image data.
                                                                       # Use reshape to make it a h,w,3 image 
   return (fnum,a)

f = open('../Final_Project/calibration.pckl', 'rb')
cameraMatrix, distCoeffs = pickle.load(f)
f.close()

aruco_dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_7X7_250)
parameters = cv2.aruco.DetectorParameters_create()

if __name__ == '__main__':
    r = redis.Redis('140.182.152.47', port=6379, db=0)
    key = 0
    last_time = 0
    delta_time = 0
    time_temp = 0
    while key != 27:
        time_temp = time()
        delta_time = int((time_temp - last_time) * 1000)
        last_time = time_temp
        fnum, img = fromRedis(r,'latest')
        print(f"read image with shape {img.shape} frame={fnum} delta={delta_time} mS frame rate={int(1/(delta_time/1000))} fps")
        
        #gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(img, aruco_dictionary, parameters=parameters)
        img = cv2.aruco.drawDetectedMarkers(image=img, corners=corners, ids=ids, borderColor=(0, 255, 0))

        if ids is not None:
            rvecs, tvecs = cv2.aruco.estimatePoseSingleMarkers(corners, .02652 , cameraMatrix, distCoeffs)
            for rvec, tvec in zip(rvecs, tvecs):
                cv2.aruco.drawAxis(img, cameraMatrix, distCoeffs, rvec, tvec, .030)

        cv2.imshow('image', img)

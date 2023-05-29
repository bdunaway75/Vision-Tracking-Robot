from AlphaBot2 import AlphaBot2
import struct
import redis
import numpy as np
import cv2
import os
import pickle

Ab = AlphaBot2()

def toRedis(r,a,n,fnum):
   h, w = a.shape[:2]             # Shape of the h, w and not the 3 colors in the depth of the image
   shape = struct.pack('>II',h,w) # Pack the height and the width variables into variable shape
                                  # Big Endian
   encoded = shape + a.tobytes()  # concatenate the shape variable and the encoded image
   r.hmset(n,{'frame':fnum,'image':encoded})
   return

if __name__ == '__main__':

    r = redis.Redis('140.182.152.47', port=6379, db=0)
    cam = cv2.VideoCapture(0)
    cam.set(3, 320)
    cam.set(4, 240)

    if os.path.exists('../Final_Project/calibration.pckl'):
        f = open('../Final_Project/calibration.pckl', 'rb')
        cameraMatrix, distCoeffs = pickle.load(f)
        f.close()
    else:
        print("You need to calibrate the camera you'll be using. See calibration script.")

    aruco_dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_7X7_250)
    parameters = cv2.aruco.DetectorParameters_create()

    key = 0
    count = 0
    maximum = 25
    integral = 0
    previous_error = 0

    while key != 27:

        ret, img = cam.read()
        toRedis(r, img, 'latest',count)
        count += 1
        print(count)

        aruco_dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_7X7_250)
        parameters = cv2.aruco.DetectorParameters_create()

        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(img, aruco_dictionary, parameters=parameters)
        if ids is not None:
            # print("4 corners:\n", corners[0][0])
            c1 = corners[0][0][0]
            c2 = corners[0][0][1]
            c3 = corners[0][0][2]
            c4 = corners[0][0][3]
            # print("corners:",c1,c2,c3,c4)

            y = (corners[0][0][0][1], corners[0][0][1][1], corners[0][0][2][1], corners[0][0][3][1])
            print(y)

            x = (corners[0][0][0][0] + corners[0][0][1][0] + corners[0][0][2][0] + corners[0][0][3][0])
            position = (x / 4)

            # # PID Loop
            error = position - 160
            # print("error = ", error)
            integral += error
            derivative = error - previous_error 
            previous_error = error

            pterm = error * 0.05  # 0.08
            # iterm = 0
            iterm = integral * 0.0001
            # dterm = 0
            dterm = derivative * 0.05

            output = pterm + iterm + dterm
            # print("output = ", output)

            if (output > maximum):
                output = maximum
            if (output < -maximum):
                output = -maximum
        
            if (output < 0):
                left = maximum + output      # left < right
                right = maximum              # right wheel spinning faster than left
                Ab.setMotor(-right, -left)   # result -> left turn
            else: #  output > 0 
                left = maximum               # right > left
                right = maximum - output     # left wheel spinning faster than left
                Ab.setMotor(-right, -left)   # result -> right turn
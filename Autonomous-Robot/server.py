#!/usr/bin/env python3
from curses_interface import curses_inter
import struct
import redis
import numpy as np
import cv2
import os
import pickle
import time

Curses = curses_inter()

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
    maximum = 25        # variable for PID loop
    integral = 0        # variable for PID loop
    previous_error = 0  # variable for PID loop
    flag = False
    stop_count = 0

    while True:

        ret, img = cam.read()
        toRedis(r, img, 'latest',count)
        count += 1
        Curses.stdscr.addstr(1, 1, "Images sent through redis: ")
        Curses.stdscr.addstr(1, 28, str(count))

        start_time = time.perf_counter()

        if Curses.key == 'm':
        # if Curses.checking_keys() == 'm':  # Enter manual mode
            while True:
                start_time = time.perf_counter()
                if Curses.checking_keys() == 'q':
                    Curses.stdscr.addstr(5, 1, 'quit manual mode')
                    break
                Curses.manual()
                Curses.stdscr.addstr(5, 1, 'manual mode         ')
                runtime = (time.perf_counter() - start_time)
                Curses.stdscr.addstr(3, 1, 'manual mode runtime: ')
                Curses.stdscr.addstr(3, 22, str(runtime))

        if Curses.key == 'a':
        # if Curses.checking_keys() == 'a':  # Enter autonomous mode
            while True:
                start_time = time.perf_counter()
                Curses.stdscr.addstr(5, 1, 'autonomous mode     ')

                if Curses.checking_keys() == 'q':
                    Curses.stdscr.addstr(5, 1, 'quit autonomous mode')
                    break

                Curses.Ab.avoid()

                ret, img = cam.read()
                toRedis(r, img, 'latest',count)
                count += 1
                Curses.stdscr.addstr(1, 1, "Images sent through redis: ")
                Curses.stdscr.addstr(1, 28, str(count))
                
                aruco_dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_7X7_250)
                parameters = cv2.aruco.DetectorParameters_create()

                corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(img, aruco_dictionary, parameters=parameters)
                if ids is not None:

                    y = (corners[0][0][3][1] - corners[0][0][0][1])  # y = bottom corner - top corner
                    Curses.stdscr.addstr(3, 60, str(y))
                    if y >= (240*0.17):   # y >= 40.8
                        flag = True

                    x = (corners[0][0][0][0] + corners[0][0][1][0] + corners[0][0][2][0] + corners[0][0][3][0])
                    position = (x / 4)
                    
                    # PID Loop
                    error = position - 160                # when arUco is centered, error is 0
                    Curses.stdscr.addstr(7, 1, "error value: ")
                    Curses.stdscr.addstr(7, 15, str(error))

                    integral += error                     # an accumulation of all error values -> large number
                    derivative = error - previous_error   # difference between each previous error -> small number
                    previous_error = error

                    pterm = error * 0.05  # 0.08
                    # iterm = 0
                    iterm = integral * 0.0001
                    # dterm = 0
                    dterm = derivative * 0.05

                    output = pterm + iterm + dterm
                    Curses.stdscr.addstr(9, 1, "output value: ")
                    Curses.stdscr.addstr(9, 14, str(output))

                    if (output > maximum):
                        output = maximum
                    if (output < -maximum):
                        output = -maximum
        
                    if (output < 0):  
                        if flag == True:
                            left = (maximum + output) / 4        
                            right = maximum / 4                  
                            Curses.Ab.setMotor(-right, -left)
                            flag = False     
                        else:
                            left = (maximum + output)              # left < right
                            right = maximum                        # right wheel spinning faster than left
                            Curses.Ab.setMotor(-right, -left)      # result -> left turn
                            flag = False
                    else:  # output > 0
                        if flag == True:
                            left = maximum / 4                     
                            right = (maximum - output) / 4         
                            Curses.Ab.setMotor(-right, -left)
                            flag = False      
                        else:
                            left = maximum                         # right > left
                            right = maximum - output               # left wheel spinning faster than left
                            Curses.Ab.setMotor(-right, -left)      # result -> right turn
                            flag = False
                else:
                    # Curses.Ab.stop()
                    stop_count += 1
                    if stop_count % 10 == 0:
                        Curses.Ab.stop()
                        stop_count = 0
                    
                runtime = (time.perf_counter() - start_time)
                Curses.stdscr.addstr(3, 1, 'autonomous mode runtime: ')
                Curses.stdscr.addstr(3, 26, str(runtime))

        if Curses.checking_keys() == 't':  # test
            Curses.stdscr.addstr(1, 60, 'This is a test :)')

        runtime = (time.perf_counter() - start_time)
        Curses.stdscr.addstr(3, 1, 'main loop runtime: ')
        Curses.stdscr.addstr(3, 20, str(runtime))

import os
import pickle
import cv2

# Check for camera calibration data
if not os.path.exists('../Final_Project/calibration.pckl'):
    print("You need to calibrate the camera you'll be using. See calibration script.")
    exit()
else:
    f = open('../Final_Project/calibration.pckl', 'rb')
    cameraMatrix, distCoeffs = pickle.load(f)
    f.close()
    if cameraMatrix is None or distCoeffs is None:
        print("Calibration issue. Remove ./calibration.pckl and recalibrate your camera")
        exit()

aruco_dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_7X7_250)
parameters = cv2.aruco.DetectorParameters_create()
capture = cv2.VideoCapture(0)

while True:
    ret, frame = capture.read()
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(frame, aruco_dictionary, parameters=parameters)
    if ids is not None:
        rvecs, tvecs = cv2.aruco.estimatePoseSingleMarkers(corners, .02652 , cameraMatrix, distCoeffs)
        print(rvecs, tvecs)

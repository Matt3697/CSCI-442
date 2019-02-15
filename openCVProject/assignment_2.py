'''
Authors: Matthew Sagen, Hugh Jackovich
'''

import cv2
import numpy as np

#set up windows
cv2.namedWindow("Original", cv2.WINDOW_KEEPRATIO)
cv2.namedWindow("HSV", cv2.WINDOW_KEEPRATIO)
cv2.namedWindow("Black/White", cv2.WINDOW_KEEPRATIO)
cv2.namedWindow("Erosion", cv2.WINDOW_KEEPRATIO)
cv2.namedWindow("Dilation", cv2.WINDOW_KEEPRATIO)
cv2.namedWindow("Video", cv2.WINDOW_KEEPRATIO)
cv2.namedWindow("Diff", cv2.WINDOW_KEEPRATIO)

cv2.moveWindow("Original", 0, 0)
cv2.moveWindow("HSV", 400, 0)
cv2.moveWindow("Black/White", 800, 0)
cv2.moveWindow("Erosion", 0, 400)
cv2.moveWindow("Dilation", 300, 400)
cv2.moveWindow("Video", 600, 400)
cv2.moveWindow("Diff", 900, 400)

#initialize variables so we can use 'em
hsv = 0
minHSV = np.array([0, 0, 0])
maxHSV = np.array([0, 0, 0])
res = [0, 0, 0]
kernel = np.ones((5,5), np.uint8)

def nothing(x):
    pass

#set new pixel to track when clicked (only for HSV window)
def onMouse(evt, x, y, flags, pic):
    if evt==cv2.EVENT_LBUTTONDOWN:
        global res
        res = hsv[y][x]
        print(str(x) + ", " + str(y))
        print(res)

#set scalar values for tracking every loop
def setScals(h, s, v):
    global res, minHSV, maxHSV
    minHSV = np.array([res[0] - h, res[1] - s, res[2] - v])
    maxHSV = np.array([res[0] + h, res[1] + s, res[2] + v])

#create trackbars
cv2.createTrackbar("Hue", "HSV", 0, 255,nothing)
cv2.createTrackbar("Sat", "HSV", 0, 255,nothing)
cv2.createTrackbar("Val", "HSV", 0, 255,nothing)
cv2.createTrackbar("1", "HSV", 0, 255,nothing)
cv2.createTrackbar("2", "HSV", 0, 255,nothing)
cv2.createTrackbar("3", "HSV", 0, 255,nothing)
cv2.setMouseCallback("HSV", onMouse, hsv)

cap = cv2.VideoCapture(0)
rval, frame = cap.read()

#set up blank images
blank1 = np.float32(frame)
blank2 = np.float32(frame)
img = np.float32(frame)
diff = np.float32(frame)

while True:

    val, img = cap.read()
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) #convert to HSV
    black_white = cv2.inRange(hsv, minHSV, maxHSV) #create black and white image
    erode = cv2.erode(black_white, kernel, iterations=2) 
    dilate = cv2.dilate(erode, kernel, iterations=2) 

    blur = cv2.GaussianBlur(img,(5,5),0)
    cv2.accumulateWeighted(blur, blank1, .4)
    res1 = cv2.convertScaleAbs(blank1)
    diff = cv2.absdiff(img, res1)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, gray = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)
    gray = cv2.GaussianBlur(gray,(5,5),0)
    _, gray = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cv2.drawContours(frame, contours, -1, (0,255,0), 3)
    cv2.imshow("Video", frame)
    cv2.imshow("Diff", gray)


    #create images in windows
    cv2.imshow("Original", img)
    cv2.imshow("HSV", hsv)
    cv2.imshow("Black/White", black_white)
    cv2.imshow('Erosion', erode)
    cv2.imshow('Dilation', dilate)
    k = cv2.waitKey(1)
    if k == 27:
        break

    #get current positions of three trackbars
    h = cv2.getTrackbarPos('Hue', 'HSV')
    s = cv2.getTrackbarPos('Sat', 'HSV')
    v = cv2.getTrackbarPos('Val', 'HSV')

    #update tracking scalars
    setScals(h, s, v)

cv2.destroyAllWindows()

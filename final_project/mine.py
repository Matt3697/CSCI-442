from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import maestro
import numpy as np
import client

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640,480))
 
#Set motor enums
BODY = 0
MOTORS = 1
TURN = 2
HEADTURN = 3
HEADTILT = 4
SHOULDER = 6
HAND = 11
ELBOW = 8

#Set default motor values
tango = maestro.Controller()

#Assign initial values to motors
tango.setTarget(HEADTURN, 6000)
tango.setTarget(HEADTILT, 6000)
tango.setTarget(TURN, 6000)
tango.setTarget(BODY, 6000)
tango.setTarget(SHOULDER, 6000)
tango.setTarget(HAND, 6000)
#tango.setTarget(ELBOW, 6000)

body = 5700
headTurn = 6000
headTilt = 6000
turn = 6000
maxMotor = 6800
maxLeftTurn = 7000
maxRightTurn = 5200
motors = 5200
shoulder = 6000
hand = 6000
elbow = 6000

#global flags/vars
bodyFlag = True
turnFlag = -1
i = 0

#values for finding orange line with hsv
lower_yellow_bound = np.array([20, 50, 50], dtype="uint8")
upper_yellow_bound = np.array([39, 250, 255], dtype="uint8")
lower_pink_bound = np.array([150, 10, 180], dtype="uint8") #155, 15, 185
upper_pink_bound = np.array([170, 125, 255], dtype="uint8") #175, 120, 255
lower_white_bound = np.array([0, 0, 235], dtype="uint8")
upper_white_bound = np.array([255, 15, 255], dtype="uint8")
lower_green_bound = np.array([40, 50, 50], dtype="uint8")
upper_green_bound = np.array([80, 255, 255], dtype="uint8")


time.sleep(2)

#Returns the desired image for a given stage
def getFrame(stage):
    hsv = []
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array

        if stage != -1:
            blur = cv2.GaussianBlur(image, (5, 5), 1)
            #image = cv2.fastNlMeansDenoisingColored(image,None,10,10,7,1)
            hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
            #element = cv.getStructuringElement(dilatation_type, (2*dilatation_size + 1, 2*dilatation_size+1), (dilatation_size, dilatation_size))
            #dilatation_dst = cv.dilate(src, element)
            #image = cv2.Canny(mask, 100, 50) #For safe keeping

        if stage == 0:
            image = cv2.inRange(hsv, lower_yellow_bound, upper_yellow_bound)
        elif stage == 1:
            image = cv2.inRange(hsv, lower_pink_bound, upper_pink_bound)
        elif stage == 2:
            image = cv2.inRange(hsv, lower_white_bound, upper_white_bound)
        elif stage == 3:
            image = cv2.inRange(hsv, lower_green_bound, upper_green_bound)
        break

    return image


#Shows the frame
def showFrame(image, flag):
    cv2.imshow("Main Camera", image)
    
    #Apparently fixed an issue with a frozen frame not being replaced by new one.
    if flag:
        key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            shutdown()


#Stops all motors but not program, had an issue with stopping a motor, this worked.
def stop():
    motors = 6000
    turn = 6000
    headTilt = 6000
    tango.setTarget(MOTORS, motors)
    tango.setTarget(TURN, turn)
    tango.setTarget(HEADTILT, headTilt)
    tango.setTarget(BODY, 6000)
    tango.setTarget(HAND, 6000)
    tango.setTarget(SHOULDER, 6000)
    rawCapture.truncate(0)


#Shuts down all motors to their original origin and ends program
def shutdown():
    motors = 6000
    turn = 6000
    headTilt = 6000
    tango.setTarget(MOTORS, motors)
    tango.setTarget(TURN, turn)
    tango.setTarget(HEADTILT, headTilt)
    tango.setTarget(BODY, 6000)
    tango.setTarget(HAND, 6000)
    tango.setTarget(SHOULDER, 6000)
    client.client.killSocket()
    rawCapture.truncate(0)
    quit()


#Search positions for finding a human, rotates accordingly
def nextSearchPosition():
        positions = [(6000, 6000, 6000), (6000, 7000, 6500), (6800, 7000, 6500), (6000, 7000, 6500), (5200, 7000, 6500), (6000, 6000, 6000),
                        (5200, 5000, 5500), (6000, 5000, 5500), (6800, 5000, 5500)] #tilt, turn, bodyturn
        global headTilt, headTurn, i
        headTilt = positions[i%9][0]
        headTurn = positions[i%9][1]
        tango.setTarget(HEADTURN, headTurn)
        tango.setTarget(HEADTILT, headTilt)
        tango.setTarget(BODY, positions[i%9][2])
        time.sleep(1.5)
        i += 1


#Centers the body of the robot towards a square object
def centerBody(xabs, yabs, xdist):
    global body, motors, turn, bodyFlag, headTilt, headTurn

    if(headTurn == 5000):
        body = 5400
        turn = 5000
        tango.setTarget(MOTORS, motors)
        tango.setTarget(TURN, turn)
        time.sleep(.8)

    elif(headTurn == 7000):
        body = 6600
        turn = 7000
        tango.setTarget(MOTORS, motors)
        tango.setTarget(TURN, turn)
        time.sleep(.8) 
    elif(xabs > 75):
        if(xdist > 0): #turn robot left
            if(body < 6000): #if was previously turned other way
                body = 6000
            if(body == 6000):
                body = 6600
            if(body == 6600): #already turned body, so turn machine
                turn = 7000
                #tango.setTarget(MOTORS, motors)
                tango.setTarget(TURN, turn)
                time.sleep(0.5)
                body = 6000
        elif(xdist < 0): # turn robot right
                if(body > 6000): # if was previously turned other way
                    body = 6000
                if(body == 6000):
                    body = 5550 
                if(body == 5550):
                    turn = 5000
                    tango.setTarget(MOTORS, motors)
                    tango.setTarget(TURN, turn)
                    time.sleep(0.5)
                    body = 6000

    bodyFlag = False
    tango.setTarget(TURN, 6000)
    tango.setTarget(BODY, 6000)
    tango.setTarget(HEADTURN, 6000)
        

#Centers the screen on a square object
def centerScreen(xabs, yabs, xdist, ydist):
    if((xabs > 60) or (yabs > 50)):
        xdist = xdist + int(xdist*.3)
        ydist = ydist + int(ydist*.3)
        tango.setTarget(HEADTURN, 6000 + (xdist*2))
        tango.setTarget(HEADTILT, 6000 + (int(ydist*2.5)))
    elif((xabs < 60) and (yabs > 50)):
        return True
    return False


#Finds the highest white pixel y value.
def findHighestY(img):
   white_pixels = np.argwhere(img >= 254)
   highest_y = 0
   for y, x in white_pixels:
       if y > highest_y:
           highest_y = y
   return highest_y


#Method for avoiding white objects
def avoidWhite():
    global turnFlag
    img = getFrame(2)
    showFrame(img, False)
    high_y = findHighestY(img)
    x, y = findCoG(img, True)
    size = len(np.argwhere(img >= 254))
    print(x, y, high_y)

    if high_y >= 400 and 370 > x > 270 and y > 260:
        print("backwards")
        if turnFlag == 3:
            tango.setTarget(TURN, 5000)
            time.sleep(1)
            tango.setTarget(TURN, 6000)
            turnFlag == 4
            return 1
        #tango.setTarget(MOTORS, 6000)
        #time.sleep(0.1)
        tango.setTarget(MOTORS, 7000)
        time.sleep(0.8)
        tango.setTarget(MOTORS, 6000)
        turnFlag == 3

    if 290 > x > 120 and y > 150:
        turnFlag = 1
        print("right turn")
        tango.setTarget(TURN, 5000)
        time.sleep(.85)
        tango.setTarget(TURN, 6000)
    elif 520 > x > 350 and y > 150:
        turnFlag = 0
        print("left turn")
        tango.setTarget(TURN, 7000)
        time.sleep(.85)
        tango.setTarget(TURN, 6000)
    #print("size", size)
    # < 18000
    if y <= 60 or size < 9500:
        if turnFlag == 1:
            time.sleep(1.5)
            tango.setTarget(TURN, 7000)
            time.sleep(.85)
            tango.setTarget(TURN, 6000)
            turnFlag = -1
        elif turnFlag == 0:
            time.sleep(1.5)
            tango.setTarget(TURN, 5000)
            time.sleep(.85)
            tango.setTarget(TURN, 6000)
            turnFlag = -1

    rawCapture.truncate(0)
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        shutdown()
        return 1


#function to determine center of gravity of white objects
def findCoG(img, flag):
    white_pixels = np.argwhere(img >= 254)
    size = len(white_pixels)
    sumX = 0
    sumY = 0
    if size < 3500:
        return -1, -1
    for y, x in white_pixels:
        if flag:
            if y > 160:
                if 590 > x > 50:
                    sumX += x
                    sumY += y
                else:
                    size = size - 1
            else:
                size = size - 1
        else:
            if y > 125:
                sumX += x
                sumY += y
            else:
                size = size - 1

    if(size > 0):
        sumX = sumX / size
        sumY = sumY / size
    else:
        return -1, -1
    return sumX, sumY


#Finds white pixels near the center of the image, returns if found 150
def findCenterWhitePixels(img):
    white_pixels = np.argwhere(img >= 254)
    count = 0
    for y, x in white_pixels:
        if y > 180:
            if 350 > x > 290:
                count += 1
    if count > 19000:
        return 1
    else:
        return 0


#Method to ignore noise while turning
def threshold():
    img = getFrame(2)
    white_pixels = np.argwhere(img >= 254)
    size = len(white_pixels)
    rawCapture.truncate(0)

    if size < 100000:
        if findCenterWhitePixels(img):
            return 1
        return 0
    else:
        return 1


#Find yellow line and cross it
def init_stage():
    headTilt = 4000
    tango.setTarget(HEADTILT, headTilt)
    tango.setTarget(TURN, maxLeftTurn)
    flag = False

    while True:
        if not flag:
            tango.setTarget(TURN, maxLeftTurn)
        img = getFrame(0)
        showFrame(img, False)
        y = findHighestY(img)
        x, yx = findCoG(img, False)
        
        if y > 420 and flag:
            time.sleep(.93)
            tango.setTarget(MOTORS, 6000)
            client.client.sendData("Rocky area ahead")
            rawCapture.truncate(0) 
            break
        
        if 270 <= x <= 370:
            print("Forward ini")
            #go forward toward the line
            if not flag:
                tango.setTarget(TURN, 6000)
                tango.setTarget(TURN, 5000)
                time.sleep(.4)
            
            tango.setTarget(TURN, 6000)
            tango.setTarget(MOTORS, 5000)
            flag = True
        else:
            flag  = False

        rawCapture.truncate(0)
        if threshold() and flag:
            if avoidWhite():
                break

        key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
                shutdown()
                break


#Avoid rocks, find and cross pink line
def stage_one():
    flag = False
    while True:
        avoidWhite()
        
        tango.setTarget(MOTORS, 5000)

        #Find PINK line
        img = getFrame(1)
        y = findHighestY(img)
        x, yx = findCoG(img, False)
        print("STAGE ONE:")
        print(x, yx, y)

        if(270 <= x <= 370):
            flag = True
        else:
            flag = False

        if x > 480 and yx > 160:
            print("FIRST")
            tango.setTarget(TURN, 5000)
            time.sleep(1)
            tango.setTarget(TURN, 6000)
        elif 0 < x < 160 and yx > 160:
            print("SECOND")
            tango.setTarget(TURN, 7000)
            time.sleep(1)
            tango.setTarget(TURN, 6000)

        if y > 380 and flag:
            tango.setTarget(MOTORS, 5000)
            time.sleep(2.3)
            tango.setTarget(MOTORS, 6000)
            client.client.sendData("Mining area reached")
            rawCapture.truncate(0) 
            break
        
        rawCapture.truncate(0)
        key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            shutdown()
            break

#Find human and grab ice
def stage_two():
    findHumanFlag = True
    distFlag = True
    tango.setTarget(HEADTILT, 6300)

    while True:
        if findHumanFlag:
            nextSearchPosition()
        img = getFrame(-1)
        showFrame(img, True)
        face_cascade = cv2.CascadeClassifier('data/haarcascades/haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(img, 1.3, 4)
        if(len(faces) != 0):
                if(findHumanFlag):
                        client.client.sendData("Howdy Human")
                        findHumanFlag = False
                x,y,w,h = faces[0]
                xcenter = x + int((w/2))
                ycenter = y + int((h/2))
                xdist = 320 - xcenter
                ydist = 240 - ycenter
                xabs = abs(320 - xcenter)
                yabs = abs(240 - ycenter)
                if(bodyFlag):
                    centerBody(xabs, yabs, xdist)
                else:
                    centerScreen(xabs, yabs, xdist, ydist)
                    if(distFlag):
                        if(w*h < 19000 or w*h > 24000):
                            if(w*h < 19000): #move forwwards
                                temp = (19000-w*h) / 5400
                                motors = 5500
                                tango.setTarget(MOTORS, motors)
                                time.sleep(temp)
                            elif(w*h > 24000): #move backwards
                                temp = (w*h-24000)/50000
                                motors = 6500
                                tango.setTarget(MOTORS, motors)      
                                time.sleep(temp)
                            distFlag = False
                            motors = 6000
                            tango.setTarget(MOTORS, motors)
                            client.client.sendData("Give me ice")
                            break

        rawCapture.truncate(0)
        key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            shutdown()
            break
    rawCapture.truncate(0)
    #Grab ice with arm
    init_flag = True
    while True:
        #maybe look right/down a bit
        img = getFrame(3)
        showFrame(img, False)
        if(init_flag):
            tango.setTarget(ELBOW, 7000)
            tango.setTarget(SHOULDER, 7200)
        x, y = findCoG(img, False)
        if x != -1 and y != -1:
            time.sleep(1.8)
            tango.setTarget(HAND, 10000)
            rawCapture.truncate(0)
            break
        
        rawCapture.truncate(0)
        key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            shutdown()
            break

#Find and cross pink line again
def stage_three():
    headTilt = 4000
    tango.setTarget(HEADTILT, headTilt)
    tango.setTarget(TURN, maxLeftTurn)
    time.sleep(.1)
    flag = False

    while True:
        if not flag:
            tango.setTarget(TURN, maxLeftTurn)
        img = getFrame(1)
        showFrame(img, False)
        y = findHighestY(img)
        x, yx = findCoG(img, False)

        if y > 420 and flag:
            time.sleep(1)
            tango.setTarget(MOTORS, 6000)
            client.client.sendData("Rocky area ahead")
            rawCapture.truncate(0)
            break

        if 270 <= x <= 370:
            print("Forward ini")
            if not flag:
                tango.setTarget(TURN, 6000)
                tango.setTarget(TURN, 5000)
                time.sleep(.43)
            #go forward toward the line
            tango.setTarget(TURN, 6000)
            tango.setTarget(MOTORS, 5200)
            flag = True
        else:
            flag = False

        rawCapture.truncate(0)
        if threshold() and flag:
            if avoidWhite():
                break

        key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
                shutdown()
                break


#Find and cross yellow line again
def stage_four():
    while True:
        avoidWhite()
        tango.setTarget(MOTORS, 5200)

        #Find yellow line
        img = getFrame(0)
        showFrame(img, False)
        y = findHighestY(img)
        x, yx = findCoG(img, False)

        if y > 400:
            time.sleep(1.3)
            tango.setTarget(MOTORS, 6000)
            client.client.sendData("Starting area reached")
            rawCapture.truncate(0)
            break
        
        rawCapture.truncate(0)
        key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            shutdown()
            break

#Find bin and drop the ice in it
def final_stage():
    headTilt = 4000
    tango.setTarget(HEADTILT, headTilt)
    flag = False
    time_flag = True
    orientate_flag = -1
    right_hand_side = False
    timer = 0

    while True:
        img = getFrame(3)
        showFrame(img, False)
        x, y = findCoG(img, False)

        #Uses center of gravity to compute proper orientation
        if flag:
            if x == -1 and y == -1:
                # if orientate_flag:
                #     orientate(False)
                # elif not orientate_flag:
                #     orientate(True)
                time.sleep(.5)
                stop()
                rawCapture.truncate(0)
                break

        if x == -1 and y == -1:
            if time_flag:
                timer = time.time()
                time_flag = False
            elasped_time = time.time() - timer
            if elasped_time > 3:
                flag = False
                time_flag = True

        if 290 <= x <= 350:
            if not flag:
                pass
                client.client.sendData("Found the Bin")
            #go forward toward the bin
            tango.setTarget(TURN, 6000)
            tango.setTarget(MOTORS, 5200)
            flag = True

        elif 0 < x < 300:
            print("LEFT")
            tango.setTarget(TURN, 7000)
            time.sleep(.75)
            tango.setTarget(TURN, 6000)
            right_hand_side = True
            # print("Howdy")
        elif x > 380:
            print("RIGHT")
            tango.setTarget(TURN, 5000)
            time.sleep(.75)
            tango.setTarget(TURN, 6000)
            # right_hand_side = True
                
        if not flag:
            tango.setTarget(TURN, 7000)

        rawCapture.truncate(0)
        key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop 
        if key == ord("q"):
            shutdown()
            break

    #Dropping ice in Bin
    tango.setTarget(SHOULDER, 7200)
    if right_hand_side:
        tango.setTarget(BODY, 9500)
    else:
        tango.setTarget(BODY, 8000)
    time.sleep(.8)
    client.client.sendData("Dropping. And Done.Goodbye")
    tango.setTarget(HAND, 6000)


#Main method for calling stages in order, though, sometimes its nice to go back.
def main():
    #shutdown()
    print("Init stage")
    init_stage()

    print("Stage 1")
    stage_one()

    print("Stage 2")
    stage_two()

    print("Stage 3")
    stage_three()

    print("Stage 4")
    stage_four()

    print("Final Stage")
    final_stage()
  
    shutdown()

main()


#tester method
def test():
    final_stage()
    shutdown()

# test()
# final_stage()
# shutdown()
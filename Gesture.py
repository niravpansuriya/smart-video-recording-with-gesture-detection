
# This program will process all the frames and will find the gesture,
# Once it will find the gesture, it will store all next frames(basically video), till it will not get next gesture.
# Here gesture is three fingurs.


import cv2
import numpy as np
import math
import time
import urllib.request as ur


#If you want to capture video from Webcamera.
#cap = cv2.VideoCapture(0)

#This is the image address of the ip which is from IP2WEBCAM android application.
url='http://192.168.43.33:8081/shot.jpg?rnd=45482'

count=0
fin=0

while(True):

    imgResp = ur.urlopen(url) #getting frame

    imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8) #convert frame to np array
    img = cv2.imdecode(imgNp, -1)

    cv2.rectangle(img,(300,300),(200,200),(0,255,0),0) #crop image
    crop_img = img[100:300, 100:300]

    grey = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY) #convert image into gray scale from RGB
    
    value = (35, 35) #this is new size for gaussian blurred filtered image
    blurred = cv2.GaussianBlur(grey, value, 0)	#applying low pass gausian filter for reduce noise. It is helpful for find edges.
    _, thresh1 = cv2.threshold(blurred, 127, 255,
                               cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU) 
    cv2.imshow('Thresholded', thresh1)

    gg,contours, hierarchy = cv2.findContours(thresh1.copy(),cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) #find contours. 
    # Contours are the curves joining all the continuous points.

    # Finding largest contour. Basically this will remove small contours those are there beacause of noise.
    # It will find the palm of hand.
    max_area = -1
    for i in range(len(contours)):
        cnt=contours[i]
        area = cv2.contourArea(cnt)
        if(area>max_area):
            max_area=area
            ci=i
    cnt=contours[ci]

    x,y,w,h = cv2.boundingRect(cnt) # getting rectangle around palm (largest contour) 
    cv2.rectangle(crop_img,(x,y),(x+w,y+h),(0,0,255),0) 

    hull = cv2.convexHull(cnt) # finding hull in palm. Hull in plam is space between two fingures.
    drawing = np.zeros(crop_img.shape,np.uint8) # creating black canvas
    cv2.drawContours(drawing,[cnt],0,(0,255,0),0) # this will draw contours on black canvas.
    cv2.drawContours(drawing,[hull],0,(0,0,255),0) # this will hull contours on black canvas.
    #hull = cv2.convexHull(cnt,returnPoints = False)
    
    # Now we have hull. Any deviation of the object from this hull can be considered as convexity defect.
    defects = cv2.convexityDefects(cnt,hull) # finding points of convexity defect
    # Here defects is matrix in which is each row contains [starting_point,ending_point,furthest-point,approx distance to furthest_point] of hull

    # Find the number of fingures.
    count_hulls = 0 
    cv2.drawContours(thresh1, contours, -1, (0,255,0), 3)

    try:
     for i in range(defects.shape[0]):
         s,e,f,d = defects[i,0]
         start = tuple(cnt[s][0]) 
         end = tuple(cnt[e][0])
         far = tuple(cnt[f][0])

	 # finding the angle between two fingures
         a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2) +
         b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
         c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
         angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57

         if angle <= 90: #if angle is less than 90, then it is high chances that those are fingures
             count_hulls += 1
             cv2.circle(crop_img,far,1,[0,0,255],-1)
         #dist = cv2.pointPolygonTest(cnt,far,True)
         cv2.line(crop_img,start,end,[0,255,0],2)
         #cv2.circle(crop_img,far,5,[0,0,255],-1)


     # no_of_fingures = count_hulls + 1
     if count_hulls == 1:

         cv2.putText(img,"", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)

     elif count_hulls == 2:

        # Whenever the are 3 fingers on the screen photo will be clicked.
        str = "Gesture Detected"
        for i in range(30): # this is because we don't want photo with three fingures in it. So, we will pass next 30 frames. 
             imgResp = ur.urlopen(url)
             imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
             img = cv2.imdecode(imgNp, -1)

        name = "frame%d.jpg" % count
        count=count+1
        cv2.imwrite(name, img)

        cv2.putText(img, str, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, 2)

     elif count_hulls == 3:

         cv2.putText(img,"", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)

     elif count_hulls == 4:

          cv2.putText(img,"", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
     else:
         cv2.putText(img,"", (50,50),
                     cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
     #cv2.imshow('drawing', drawing)
     #cv2.imshow('end', crop_img)
     cv2.imshow('Gesture', img)
     all_img = np.hstack((drawing, crop_img))
     #cv2.imshow('Contours', all_img)
     k = cv2.waitKey(10)
     if k == 27:
         break

    except:
        continue


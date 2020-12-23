import cv2
import numpy as np
import json
import requests as r
import time
import serial
arduino = serial.Serial('/dev/ttyACM0',9600)
def nothing(a):
    pass
 
def initializeTrackbars(intialTracbarVals,hT=720, wT=1280):
    cv2.namedWindow("Trackbars")
    cv2.resizeWindow("Trackbars", 360, 240)
    cv2.createTrackbar("Width Top", "Trackbars", intialTracbarVals[0],wT//2, nothing)
    cv2.createTrackbar("Height Top", "Trackbars", intialTracbarVals[1], hT, nothing)
    cv2.createTrackbar("Width Bottom", "Trackbars", intialTracbarVals[2],wT//2, nothing)
    cv2.createTrackbar("Height Bottom", "Trackbars", intialTracbarVals[3], hT, nothing)
 
def valTrackbars(hT=720, wT=1280):
    widthTop = cv2.getTrackbarPos("Width Top", "Trackbars")
    heightTop = cv2.getTrackbarPos("Height Top", "Trackbars")
    widthBottom = cv2.getTrackbarPos("Width Bottom", "Trackbars")
    heightBottom = cv2.getTrackbarPos("Height Bottom", "Trackbars")
    points = np.float32([(widthTop, heightTop), (wT-widthTop, heightTop),
                      (widthBottom , heightBottom ), (wT-widthBottom, heightBottom)])
    return points

def find_path(img):
    back=img.copy()
    #masking
    img_hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    img_mask=cv2.inRange(img_hsv,np.array([80,0,0]),np.array([255,128,255]))
    #warp
    h,w,c=img.shape
    pts1 = valTrackbars(h,w)
    pts2 = np.float32([[0,0],[w,0],[0,h],[w,h]])
    for x in range(4):
        cv2.circle(back,(int(pts1[x][0]),int(pts1[x][1])),15,(0,0,255),cv2.FILLED)
    mat=cv2.getPerspectiveTransform(pts1,pts2)
    img_warp=cv2.warpPerspective(img_mask,mat,(w,h))
    #center_detect    
    col_sums=np.sum(img_warp[int(img_warp.shape[0]*9/10):,:],axis=0)
    maxx=np.max(col_sums)
    minn=0.9*maxx #thresold 10%
    ind_arr=np.where(col_sums>=minn)
    center=int(np.average(ind_arr))
    img_hist=np.zeros((img.shape[0],img.shape[1],3),np.uint8)
    for x,intensity in enumerate(col_sums):
        cv2.line(img_hist,(int(x),int(img.shape[0])),(int(x),int(img.shape[1]-intensity//255)),(255,255,255),1)
    cv2.circle(img_hist,(center,img.shape[0]),20,(0,255,255),cv2.FILLED)
    cv2.circle(back,(center,img.shape[0]),20,(0,255,255),cv2.FILLED)

    #point1_detect
    col_sums=np.sum(img_warp[int(img_warp.shape[0]*7/10):int(img_warp.shape[0]*9/10),:], axis=0)
    maxx=np.max(col_sums)
    minn=0.9*maxx #thresold 10%
    ind_arr=np.where(col_sums>=minn)
    point1=int(np.average(ind_arr))

    #point2_detec
    col_sums=np.sum(img_warp[int(img_warp.shape[0]*5/10):int(img_warp.shape[0]*7/10),:], axis=0)
    maxx=np.max(col_sums)
    minn=0.9*maxx #thresold 10%
    ind_arr=np.where(col_sums>=minn)
    point2=int(np.average(ind_arr))
    point=(point1+point2)//2
    cv2.circle(img_hist,(point,img.shape[0]),10,(255,0,0),cv2.FILLED)
    cv2.circle(back,(point,img.shape[0]),10,(255,0,0),cv2.FILLED)
    if (center-point)<0:
        cv2.putText(back, "Turn Right", (w//2 -110,h-80), cv2.QT_FONT_NORMAL, 2, (255, 0, 100), 3)
    elif (center-point)//10>0:
        cv2.putText(back, "Turn Left", (w//2 -110,h-80), cv2.QT_FONT_NORMAL, 2, (255, 0, 100), 3)
    else:
        cv2.putText(back, "Straight", (w//2 -110,h-80), cv2.QT_FONT_NORMAL, 2, (255, 0, 100), 3)
    # add_path_color
    mat = cv2.getPerspectiveTransform(pts2, pts1)
    img_warp_inv=cv2.warpPerspective(img_warp,mat,(w,h))
    cv2.imshow("inv",img_warp_inv)
    cv2.imshow("no inv",img_warp)
    img_warp_inv=cv2.cvtColor(img_warp_inv,cv2.COLOR_GRAY2BGR)
    img_warp_inv[0:h // 3, 0:w] = 0, 0, 0
    imgLaneColor = np.zeros_like(img)
    imgLaneColor[:] = 0, 255, 0
    imgLaneColor = cv2.bitwise_and(img_warp_inv, imgLaneColor)
    back = cv2.addWeighted(back, 1, imgLaneColor, 0.5, 0)
    #--
    # imgLaneColor = np.zeros_like(img)
    # imgLaneColor[:] = 0, 255, 0
    # img_mask_rgb=cv2.cvtColor(img_mask,cv2.COLOR_GRAY2BGR)
    # imgLaneColor = cv2.bitwise_and(img_mask_rgb, imgLaneColor)
    # back=cv2.addWeighted(back,1,imgLaneColor,0.5,0)
    #--
    return img_hist,(center-point),back

def send_data(curve):
    if arduino.isOpen():
        if curve<0:
            arduino.write(b'2')
        elif curve>0:
            arduino.write(b'1')
        else:
            arduino.write(b'0')
    else:
        print("Serial not connected")

if __name__ == '__main__':
    intialTrackBarVals = [90, 193, 00, 240 ]
    initializeTrackbars(intialTrackBarVals)
    url="http://192.168.43.60:8080/shot.jpg"
    while True:
        img=r.get(url)
        imgr=np.array(bytearray(img.content),dtype=np.uint8)
        img = cv2.imdecode(imgr,-1)
        img = cv2.resize(img,(480,240))
        img,curve,back=find_path(img)
        send_data(curve)
        cv2.imshow("vid",back)
        cv2.waitKey(1)

# if __name__=='__main__':
#     cap=cv2.VideoCapture('video.mp4')
#     intialTrackBarVals = [330, 529, 190, 720 ]
#     initializeTrackbars(intialTrackBarVals)
#     counter=0
#     while 1:
#         counter+=1
#         if cap.get(cv2.CAP_PROP_FRAME_COUNT)==counter:
#             cap.set(cv2.CAP_PROP_POS_FRAMES,0)
#             counter=0
#         _,img=cap.read()
#         img,center,back=find_path(img)
#         #img,center=find_path(img)
#         cv2.imshow("org",back)
#         print(json.JSONEncoder().encode({"curve": [center]}))
#         if counter==100:
#             cv2.imwrite("center.jpg",back)
#         cv2.imshow("vid",img)
#         cv2.waitKey(1)
#!/usr/bin/env python
import numpy as np
import cv2
import sys
import json
import os

import pdb

'''
Reference: https://docs.opencv.org/3.4/d8/d83/tutorial_py_grabcut.html
'''

'''

TODO:
1. Fine tuning marker colors are not showing on the image 
2. Add a feature to select multuple rectangles 
3. Export the mask as a json file
4. Convert the mask to COCO format
5. Add comments to the code
6. Start annotation with the mask instead of the rectangle

'''


BLUE = [255,0,0]        # rectangle color
RED = [0,0,255]         # PR BG
GREEN = [0,255,0]       # PR FG
BLACK = [0,0,0]         # sure BG
WHITE = [255,255,255]   # sure FG

DRAW_BG = {'color' : BLACK, 'val' : 0}
DRAW_FG = {'color' : WHITE, 'val' : 1}
DRAW_PR_FG = {'color' : GREEN, 'val' : 3}
DRAW_PR_BG = {'color' : RED, 'val' : 2}

#icons

right_mouse = cv2.resize(cv2.imread('assets/right.png'), (40, 45))
left_mouse = cv2.resize(cv2.imread('assets/left.png'), (40, 45))

# setting up flags
rect = (0,0,1,1)
drawing = False         # flag for drawing curves
rectangle = False       # flag for drawing rect
rect_over = False       # flag to check if rect drawn
rect_or_mask = 100      # flag for selecting rect or mask mode
value = DRAW_FG         # drawing initialized to FG
thickness = 3           # brush thickness
spacebar = False        # flag to start segmentation
process_started = False   # flag to start processing
spacebar_pressed = False # flag to check if spacebar is pressed

def onmouse(event, x, y, flags,param):
    global img, blended_image, drawing, value, mask, rectangle, rect, rect_or_mask, ix, iy, rect_over, spacebar

    if spacebar == False:
        # Draw Rectangle
        if event == cv2.EVENT_LBUTTONDOWN:
            rectangle = True
            ix,iy = x,y

        elif event == cv2.EVENT_MOUSEMOVE:
            if rectangle == True:
                blended_image = orig.copy()
                cv2.rectangle(blended_image, (ix, iy), (x, y), BLUE, 2)
                rect = (min(ix,x),min(iy,y),abs(ix-x),abs(iy-y))
                rect_or_mask = 0

        elif event == cv2.EVENT_LBUTTONUP:
            rectangle = False
            rect_over = True
            cv2.rectangle(blended_image, (ix, iy), (x, y), BLUE, 2)
            rect = (min(ix,x),min(iy,y),abs(ix-x),abs(iy-y))
            rect_or_mask = 0
            # print(" Now press the key 'n' a few times until no further change \n")
            print(" Press spacebar to start segmentation \n")
    else:
        pass

    if spacebar == True:
        # draw touchup curves
        if event == cv2.EVENT_LBUTTONDOWN:
            if rect_over == False:
                print("first draw rectangle \n")
            else:
                drawing = True
                cv2.circle(img, (x, y),
                           thickness, value['color'], -1)
                cv2.circle(mask,(x,y),thickness,value['val'],-1)

        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing == True:
                cv2.circle(img, (x, y),
                           thickness, value['color'], -1)
                cv2.circle(mask,(x,y),thickness,value['val'],-1)

        elif event == cv2.EVENT_LBUTTONUP:
            if drawing == True:
                drawing = False
                cv2.circle(img, (x, y),
                           thickness, value['color'], -1)
                cv2.circle(mask,(x,y),thickness,value['val'],-1)
    else:
        pass

if __name__ == '__main__':

    # print documentation
    # print(__doc__)

    # Loading images
    if len(sys.argv) == 2:
        filename = sys.argv[1] # for drawing purposes
    else:
        print("No input image given")
        print("Correct Usage: python grabcut.py <filename>")
        print("Taking default image \n")
        filename = 'images/agimage_sparse.png'

    img = cv2.imread(filename)
    orig = img.copy()  # a copy of original image
    result_img = img.copy()
    blended_image = img.copy()    # output image to be shown
    
    info = np.ones((img.shape[0],230,3),np.uint8) * 255
    mask = np.zeros(img.shape[:2],dtype = np.uint8) # mask initialized to PR_BG
    output = np.zeros(img.shape,np.uint8)           # output image to be shown

    # input and output windows
    cv2.namedWindow('Annotation Window')
    cv2.setMouseCallback('Annotation Window',onmouse)

    print(" Instructions: \n")
    print(" Draw a rectangle around the object using left mouse button \n")

    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 1

    # Set the color and thickness of the text
    color = (0, 0, 0)  # black
    thickness = 2

    # Set the position of the text
    position = (45,25)
    # Write the text on the image
    cv2.putText(info, 'Instruction', position, font, scale, color, thickness, cv2.LINE_AA)

    x, y = 10, 45
    # Copy the small image onto the large image
    info[y:y+45, x:x+40] = left_mouse
    position = (45,75)
    # Write the text on the image
    cv2.putText(info, 'Draw bounding box', position, font, 0.5, (0,0,0), 1, cv2.LINE_AA)

    position = (25,125)
    cv2.putText(info, 'R - Reset', position, font, 0.5, (0,0,0), 1, cv2.LINE_AA)

    position = (25,150)
    # Write the text on the image
    cv2.putText(info, 'S - Save annotation', position, font, 0.5, (0,0,0), 1, cv2.LINE_AA)

    position = (25,175)
    # Write the text on the image
    cv2.putText(info, 'Spacebar - Segment', position, font, 0.5, (0,0,0), 1, cv2.LINE_AA)

    x, y = 10, 195
    # Copy the small image onto the large image
    info[y:y+45, x:x+40] = left_mouse
    position = (45, 225)
    # Write the text on the image
    cv2.putText(info, 'Fine tune - select BG', position,
                font, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    while(1):

        cv2.imshow('Annotation Window',output)
        k = cv2.waitKey(1)

        # key bindings
        if k == 27:         # esc to exit
            break
        elif k == ord('0'): # BG drawing
            print(" mark background regions with left mouse button \n")
            value = DRAW_BG
        elif k == ord('1'): # FG drawing
            print(" mark foreground regions with left mouse button \n")
            value = DRAW_FG
        elif k == ord('2'): # PR_BG drawing
            value = DRAW_PR_BG
        elif k == ord('3'): # PR_FG drawing
            value = DRAW_PR_FG
        elif k == ord('s'): # save image
            bar = np.zeros((blended_image.shape[0], 5, 3), np.uint8)
            res = np.hstack((blended_image, result))
            cv2.imwrite('grabcut_output.png',res)
            print(" Result saved as image \n")
        elif k == ord('r'): # reset everything
            print("Resetting \n")
            rect = (0,0,1,1)
            drawing = False
            rectangle = False
            rect_or_mask = 100
            rect_over = False
            value = DRAW_FG
            spacebar = False
            blended_image = orig.copy()
            mask = np.zeros(img.shape[:2],dtype = np.uint8) # mask initialized to PR_BG
            output = np.zeros(img.shape,np.uint8)           # output image to be shown
        elif k == 32: # 32 is spacebar # segment the image
            spacebar = True
            process_started = True
            spacebar_pressed = True

            alpha = 1.5 # Contrast control (1.0-3.0)
            beta = 0 # Brightness control (0-100)

            if (rect_or_mask == 0):                     # grabcut with rectangle box
                print("Segmentation in progress... \n")
                bgdmodel = np.zeros((1,65),np.float64)
                fgdmodel = np.zeros((1,65),np.float64)
                cv2.grabCut(orig,mask,rect,bgdmodel,fgdmodel,20,cv2.GC_INIT_WITH_RECT)
                rect_or_mask = 1
                result = cv2.imread(filename)
            elif rect_or_mask == 1:                     # grabcut with mask
                print("Fine tuning in progress... \n")
                bgdmodel = np.zeros((1,65),np.float64)
                fgdmodel = np.zeros((1,65),np.float64) 
                cv2.grabCut(orig,mask,rect,bgdmodel,fgdmodel,20,cv2.GC_INIT_WITH_MASK)
                             

        mask2 = np.where((mask==1) + (mask==3),255,0).astype('uint8')
        output = cv2.bitwise_and(orig,orig,mask=mask2)
        img_gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
        #ret, thresh = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(image=img_gray, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(image=result_img, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=cv2.FILLED, lineType=cv2.LINE_AA)

        alpha = 0.5
        result = cv2.addWeighted(result_img, 1-alpha, orig, alpha, 0)
        cv2.drawContours(image=result, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)

        if len(contours) > 0:
            # Only show instructions, if something is segmented
            if spacebar_pressed:
                spacebar_pressed = False
                print("For finer touchups:")
                print("Press 0 to draw background regions")
                print("Press 1 to draw foreground regions")
                print("Press 2 to draw probable background regions")
                print("Press 3 to draw probable foreground regions \n")

            c = max(contours, key = cv2.contourArea)
            contour_points = cv2.approxPolyDP(c, 0.01, True)
            contour_points = np.array(contour_points)
            # np.save('contour_points1.npy', contour_points)
            img_temp = orig.copy()
            alpha = 0.3  # Transparency factor.
            # Following line overlays transparent rectangle over the image
            cv2.fillPoly(img_temp, pts = [contour_points], color =(0,255,0))
            blended_image = cv2.addWeighted(img_temp, alpha, orig, 1 - alpha, 0)
            name = filename.split('\\')[-1].split('.')[0]
            path = os.path.join('annotations', name + '.txt')
            with open(path, 'w') as fh:
                for point in contour_points:
                    cv2.circle(blended_image, (point[0][0], point[0][1]), 0, (0, 0, 255), 1)
                    fh.write('{} {}\n'.format(point[0][0], point[0][1]))
        
        # If no contours are found, then reset the image
        elif(len(contours) == 0 and process_started == True):
            process_started = False
            blended_image = orig.copy()
            output = np.hstack((blended_image, info))
            print("Could not segment")
            print("Try again \n")
            print("Switched to Mask mode")
            # spacebar = False
            continue
        
        # For displaying the segmented image
        output = np.hstack((blended_image, info))
        # output = np.hstack((img, info))

    cv2.destroyAllWindows()
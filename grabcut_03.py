import cv2
import numpy as np


BLUE = [255, 0, 0]        # rectangle color


# Create a callback function for mouse events

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, img, mask, orig, orig2

    # If the left mouse button is pressed down, start drawing
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    # If the mouse is moved while the left button is pressed down, draw a rectangle 
    # on the image to show the user the area that will be segmented by GrabCut
    # don't draw multiple rectangles, just update the existing one with the new coordinates
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            img = orig2.copy()
            cv2.rectangle(img, (ix, iy), (x, y), BLUE, 2)
            rect = (min(ix, x), min(iy, y), abs(ix-x), abs(iy-y))
            rect_or_mask = 0



    # If the left mouse button is released, stop drawing and draw the rectangle
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(orig, (ix, iy), (x, y), BLUE, 2)
        rect = (min(ix, x), min(iy, y), abs(ix-x), abs(iy-y))

        # Apply GrabCut algorithm to perform background segmentation
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        cv2.grabCut(img, mask, rect, bgdModel,
                    fgdModel, 20, cv2.GC_INIT_WITH_RECT)

        # Update the mask with the new segmentation result
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        seg = cv2.bitwise_and(orig, orig, mask=mask2)

        # Display the original image and the segmented outline side by side
        side_by_side = np.concatenate((orig, seg), axis=1)
        cv2.imshow('image', side_by_side)

        cv2.waitKey(0)



# Load an image
img = cv2.imread('images/spiderman.jpg')
orig2 = img.copy()
mask = np.zeros(img.shape[:2], np.uint8)
orig = img.copy()

# Create a window and set the mouse callback function
cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_rectangle)

drawing = False

while True:
    cv2.imshow('image', img)

    # If the 'q' key is pressed, quit the program
    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()

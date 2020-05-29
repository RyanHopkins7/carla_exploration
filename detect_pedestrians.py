from __future__ import print_function
from imutils.object_detection import non_max_suppression
from imutils import paths
import numpy as np
import argparse
import imutils
import cv2

"""
This script uses histograms of oriented gradients (HOG) for the purpose of pedestrian detection.
Non-maxima supression is used to reduce the number of false positives. The HOG model being used
is the default people detector from OpenCV which uses a window size of 64x128 as recommended by
Dalal & Triggs. 

Limitations include lack of ability to detect people far away or children due to
limitations with window size.

Usage: 
    python3 detect_pedestrians.py -i <path to image directory>

Arguments:
    Path to image directory (str): the path to the directory which contains the image files to 
        perform pedestrian detection on.

Outputs:
    Overwritten image files with bounding boxes drawn on detected people.

Sources:
https://www.pyimagesearch.com/2015/11/09/pedestrian-detection-opencv/
http://lear.inrialpes.fr/people/triggs/pubs/Dalal-cvpr05.pdf
"""

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--images", required=True,
                help="path to images directory")
args = vars(ap.parse_args())

# initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# loop over the image paths
for imagePath in paths.list_images(args["images"]):
    # load the image and resize it to (1) reduce detection time
    # and (2) improve detection accuracy
    image = cv2.imread(imagePath)
    image = imutils.resize(image, width=min(400, image.shape[1]))
    orig = image.copy()

    # detect people in the image
    (rects, weights) = hog.detectMultiScale(image, winStride=(4, 4),
                                            padding=(8, 8), scale=1.05)

    # draw the original bounding boxes
    for (x, y, w, h) in rects:
        cv2.rectangle(orig, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # apply non-maxima suppression to the bounding boxes using a
    # fairly large overlap threshold to try to maintain overlapping
    # boxes that are still people
    rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
    pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)

    # draw the final bounding boxes
    for (xA, yA, xB, yB) in pick:
        cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)

    # show some information on the number of bounding boxes
    filename = imagePath[imagePath.rfind("/") + 1:]
    print("[INFO] {}: {} original boxes, {} after suppression".format(
        filename, len(rects), len(pick)))

    # save the output images
    cv2.imwrite(imagePath, image)

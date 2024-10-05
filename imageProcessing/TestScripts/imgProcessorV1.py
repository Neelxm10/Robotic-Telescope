import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

#read in test image
img = cv.imread("Photos/13_RouzbehBidshahri_PinwheelGalaxy-2429fee.png")
# # Step 1: Convert image from BGR to RGB (since OpenCV loads in BGR)
img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

#display test image in plot
plt.imshow(img)
plt.title('Native Color Image (RGB)')
plt.axis('off')  # Hide axis
plt.show()


#apply adaptive histogram equalization (CLAHE) to the LAB colour space. This is done to preserve native colours and enhance the contrast in the luminosity channel
lab_img = cv.cvtColor(img, cv.COLOR_BGR2LAB)

#split image into L, A, and B channels
l_channel, a_channel, b_channel = cv.split(lab_img)

#create CLAHE object

clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(6,6))

#apply CLAHE to the luminosity channel
l_channel_CLAHE = clahe.apply(l_channel)

#merge image channels after adjustment
lab_img_CLAHE = cv.merge((l_channel_CLAHE, a_channel, b_channel))

#convert the image back to BGR colour space
enhanced_img = cv.cvtColor(lab_img_CLAHE, cv.COLOR_LAB2BGR)

#Display alongside original image
plt.subplot(1,2,1)
plt.imshow(img)
plt.title("Native Colour Image")
plt.axis('off')

plt.subplot(1,2,2)
plt.imshow(enhanced_img)
plt.title("Contrast enhanced image in LAB Space")
plt.axis('off')

plt.show()
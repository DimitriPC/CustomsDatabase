import cv2
import pytesseract
from PIL import Image
from matplotlib import pyplot as plt

image_file = "HelloFlask/static/uploads/2/IMG_4002_STATS.JPG"
img = cv2.imread(image_file)

#https://stackoverflow.com/questions/28816046/
#displaying-different-images-with-actual-size-in-matplotlib-subplot
def display(im_path):
    dpi = 80
    im_data = plt.imread(im_path)

    height, width  = im_data.shape[:2]
    
    # What size does the figure need to be in inches to fit the image?
    figsize = width / float(dpi), height / float(dpi)

    # Create a figure of the right size with one axes that takes up the full figure
    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([0, 0, 1, 1])

    # Hide spines, ticks, etc.
    ax.axis('off')

    # Display the image.
    ax.imshow(im_data, cmap='gray')

    plt.show()

def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def noise_removal(image):
    import numpy as np
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    image = cv2.medianBlur(image, 3)
    return (image)

def thin_font(image):
    import numpy as np 
    image = cv2.bitwise_not(image)
    kernel = np.ones((2, 2),np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.bitwise_not(image)
    return (image)

def thick_font(image):
    import numpy as np 
    image = cv2.bitwise_not(image)
    kernel = np.ones((2, 2),np.uint8)
    image = cv2.dilate(image, kernel, iterations=2)
    image = cv2.bitwise_not(image)
    return (image)

#Grayscale
gray_image = grayscale(img)
cv2.imwrite("HelloFlask/static/uploads/2/gray.jpg", gray_image)

#Black and white (binarization)
thresh, im_bw = cv2.threshold(gray_image, 185, 255, cv2.THRESH_BINARY)
cv2.imwrite("HelloFlask/static/uploads/2/bw_image.jpg", im_bw)

#Inverting image 
inverted_image = cv2.bitwise_not(img)
cv2.imwrite("HelloFlask/static/uploads/2/inverted.jpg", inverted_image)

#Noise reduction
no_noise = noise_removal(im_bw)
cv2.imwrite("HelloFlask/static/uploads/2/no_noise.jpg", no_noise)

#Dilation and Erosion
eroded_image = thin_font(no_noise)
cv2.imwrite("HelloFlask/static/uploads/2/eroded_image.jpg", eroded_image)

dilated_image = thick_font(no_noise)
cv2.imwrite("HelloFlask/static/uploads/2/dilated_image.jpg", dilated_image)

#display("HelloFlask/static/uploads/2/bw_image.jpg")

no_noise = "HelloFlask/static/uploads/2/no_noise.jpg"
img = Image.open(no_noise)
ocr_result = pytesseract.image_to_string(img)
print(ocr_result)



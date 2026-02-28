import cv2
from PIL import Image
import pytesseract

im_file = "Images/134054678217081009.jpg"

im = Image.open(im_file)

im.rotate(90).show()
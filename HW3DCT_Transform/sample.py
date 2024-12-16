import sys
import cv2 as cv
import numpy as np
import math
import matplotlib.pyplot as plt

def Global_DCT(img):
    # TODO:
        # 1. Use opencv’s DCT function or numpy’s fft function or Designed according to formula
        # EX: cv.dct(img) <--> cv.idct(img) 
    pass

def Local_DCT(img, kernel_size = 8):
    #TODO:
        # 1. Use opencv’s DCT function or numpy’s fft2 function / Designed according to formula
        # 2. Decide the core size by yourself (default 8 * 8)
    pass

def frequency_Domain_filter(DCT_img):
    # TODO:
        # 1. Input the DCT transform frequency domain image
        # 2. Crop areas of concentrated energy in the image
        # 3. After outputting the result, do IDCT
    pass
    
 
if __name__ == '__main__':

    img = cv.imread(sys.argv[1], cv.IMREAD_GRAYSCALE)
    # TODO:
        # show images


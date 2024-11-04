import sys
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import os
from concurrent.futures import ThreadPoolExecutor
output_dir = './HW2Histogram_Equalization/output_images'

def Generate_Histogram(img):
    frequency = [0]*256

    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            frequency[img[i,j]]  +=1 

    return frequency

def Cumulative_Distribution_Func(frequency,num_pixels,local=False):
    cdf=[0.0]*256
    cdf_normalize=[0]*256

    for i in range(256):
        if(i==0):
            cdf[0] = frequency[0] / num_pixels
        else:
            if(local):
                cdf[i] = min(1,cdf[i-1] + frequency[i] / num_pixels )
            else:
                cdf[i] = cdf[i-1] + frequency[i] / num_pixels  

    cdf_min = min([x for x in cdf if x > 0])
    
    ##normalize
    for i in range(256):
        cdf_normalize[i] = np.round(cdf[i]*255).astype(np.uint8)

    return cdf_normalize

def draw_historgram(origin,after=None):
    values=[]
    for i in range(256):
        values.append(i)

    plt.bar(values, origin, width=0.8, edgecolor='black', color='blue', alpha=0.5, label='Original')
    if (after != None):
        plt.bar(values, after, width=0.8, edgecolor='red', color='red', alpha=0.5, label='After HE')

    plt.title('Histogram from Given image')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.legend()
    plt.show()

    del(values)
    return


def Global_HE(img):
    #TODO:
    # step 1 : Count the number of pixel occurrences (hint : numpy --> unique())
    new_img = np.zeros_like(img,dtype=np.uint8)

    height = img.shape[0]
    width = img.shape[1]

    freq = Generate_Histogram(img)
    cdf= Cumulative_Distribution_Func(freq,height*width)

    # step 2 : Calculate the histogram equalization

    for i in range(height):
        for j in range(width):
            new_img[i,j] = cdf[img[i,j]]
    
    # step 3 : Display histogram(comparison before and after equalization)
    new_freq=Generate_Histogram(new_img)
    draw_historgram(freq,new_freq)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    cv.imwrite(output_dir+'/'+'output_global.png', new_img)
    print(f"PSNR_global: {calculate_PSNR(img,new_img)}")

    return


def Local_HE(img, size=7):
    new_img = np.zeros_like(img,dtype=np.uint8)
    height=img.shape[0]
    width=img.shape[1]

    half_size = size//2

    for i in range(height):
        for j in range(width):
            area = img[max(0, i - half_size):min(height, i + half_size + 1), max(0, j - half_size):min(width, j + half_size + 1)]
            freq = Generate_Histogram(area)
            cdf = Cumulative_Distribution_Func(freq,area.size,local=True)
            new_img[i, j] = cdf[img[i, j]]

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = f"./HW2Histogram_Equalization/output_images/output_local{size}.png"
    cv.imwrite(output_path, new_img)
    print(f"PSNR_local_{size}: {calculate_PSNR(img, new_img)}")
    freq = Generate_Histogram(new_img)
    draw_historgram(freq)

    return new_img

def calculate_PSNR(original, compressed):
    mse = np.mean((original - compressed) ** 2)
    if mse == 0:
        return np.infty
    max_pixel = 255.0
    psnr = 10 * np.log10((max_pixel ** 2) / mse)
    return psnr

    
 
if __name__ == '__main__':
    #img = cv.imread("./HW2Histogram_Equalization/images/test.png", cv.IMREAD_GRAYSCALE)
    img = cv.imread("./HW2Histogram_Equalization/images/Lena.png", cv.IMREAD_GRAYSCALE)
    Global_HE(img)
    Local_HE(img,7)

    # TODO: Display histogram(comparison before and after equalization)
    
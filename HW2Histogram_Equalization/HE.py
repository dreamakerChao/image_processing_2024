import sys
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import os
output_dir = './HW2Histogram_Equalization/output_images'

def Generate_Histogram(img):
    frequency = [0]*256

    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            frequency[img[i,j]]  +=1 

    return frequency

def Cumulative_Distribution_Func(frequency):
    cdf=[]
    sum=0

    min=0
    max=0
    t=0

    for i in range(256):
        if(frequency[i] != 0):
            if(t==0):
                min=i
            if(i > max):
                max=i
            t+=1
        sum+=frequency[i]
        cdf.append(sum)

    ##normalize
    cdf_normalized=[0]*256
    for i in range(256):
        if(cdf[i]!=0):
            if(max-min!=0):
                temp = (i - min) * 255 / (max - min)
                cdf_normalized[i] = np.round(temp)

    return cdf_normalized

def draw_historgram(frequency):
    values=[]
    for i in range(256):
        values.append(i)

    plt.bar(values, frequency, width=0.8, edgecolor='black')

    plt.title('Histogram from Given image')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.show()

    del(values)
    return


def Global_HE(img):
    #TODO:
    # step 1 : Count the number of pixel occurrences (hint : numpy --> unique())
    new_img = img.copy()
    freq = Generate_Histogram(img)
    cdf= Cumulative_Distribution_Func(freq)

    draw_historgram(freq)


    # step 2 : Calculate the histogram equalization

    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            new_img[i,j] = cdf[img[i,j]]
    
    # step 3 : Display histogram(comparison before and after equalization)
    new_freq=Generate_Histogram(new_img)
    draw_historgram(new_freq)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    cv.imwrite(output_dir+'/'+'output_global.png', new_img)
    print(f"PSNR_global: {calculate_PSNR(img,new_img)}")

    return


def Local_HE(img,size=30):
    # TODO:
    padded_img = cv.copyMakeBorder(img, size // 2, size // 2, size // 2, size // 2, cv.BORDER_REFLECT)
    new_img = np.zeros_like(img)

    # step 1 : Count the number of pixel occurrences
    # step 2 : Define a square neighborhood and move the center of this area from pixel to pixel.
    # step 3 : Calculate the histogram equalization
    for i in range(0,img.shape[0],size):
        for j in range(0,img.shape[1],size):
            area = padded_img[i:i + size, j:j + size]

            freq = Generate_Histogram(area)

            cdf= Cumulative_Distribution_Func(freq)

            for x in range(i, min(i + size, img.shape[0])):
                for y in range(j, min(j + size, img.shape[1])):
                    new_img[x, y] = cdf[img[x, y]]
            
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    cv.imwrite(output_dir+'/'+f'output_local{size}.png', new_img)
    print(f"PSNR_local_{size}: {calculate_PSNR(img,new_img)}")
    return

def calculate_PSNR(original, compressed):
    mse = np.mean((original - compressed) ** 2)
    if mse == 0:
        return np.infty
    max_pixel = 255.0
    psnr = 10 * np.log10((max_pixel ** 2) / mse)
    return psnr

    
 
if __name__ == '__main__':

    img = cv.imread("./HW2Histogram_Equalization/images/Lena.png", cv.IMREAD_GRAYSCALE)
    Global_HE(img)
    Local_HE(img,max(img.shape[0],img.shape[1])//5)

    # TODO: Display histogram(comparison before and after equalization)
    
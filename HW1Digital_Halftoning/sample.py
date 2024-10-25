import sys
import cv2 as cv
import numpy as np
import matplotlib as plt

def generate_bayer_matrix(n):
    if n == 1:
        return np.array([[0, 2], [3, 1]])
    else:
        smaller_matrix = generate_bayer_matrix(n - 1)
        size = 2 ** n
        new_matrix = np.zeros((size, size), dtype=int)
        for i in range(2 ** (n - 1)):
            for j in range(2 ** (n - 1)):
                base_value = 4 * smaller_matrix[i, j]
                new_matrix[i, j] = base_value
                new_matrix[i, j + 2 ** (n - 1)] = base_value + 2
                new_matrix[i + 2 ** (n - 1), j] = base_value + 3
                new_matrix[i + 2 ** (n - 1), j + 2 ** (n - 1)] = base_value + 1
        return new_matrix
        

def generate_thresholds_matrix(bayer_matrix):
    N = bayer_matrix.shape[0]
    thresholds_matrix = np.zeros_like(bayer_matrix, int)

    for i in range(N):
        for j in range(N):
            thresholds_matrix[i,j] = (255*(bayer_matrix[i,j]+0.5))/(N**2)

    # TODO:Calculate each bayer matrix element threshold

    return thresholds_matrix

def Ordered_Dithering(img, thresholds_matrix):
    # TODO:Implementing the ordered dithering algorithm
    N = thresholds_matrix.shape[0]
    Ordered_Dithering_img = np.zeros_like(img,np.uint8)
    height,width = img.shape

    for i in range(0,img.shape[0]-N,N):
        for j in range(0,img.shape[1]-N,N):
            for k in range(N):
                for l in range(N):
                    if i + k < height and j + l < width:
                        if(img[i+k,j+l]>thresholds_matrix[k,l]):
                            Ordered_Dithering_img[i+k,j+l] = 255
                        else:
                            Ordered_Dithering_img[i+k,j+l] = 0

    return Ordered_Dithering_img

def Error_Diffusion(img):
    # TODO:Implementing the error diffusion algorithm

    return #Error_Diffusion_img

if __name__ == '__main__':

    #img = cv.imread(sys.argv[1])
    img = cv.imread("./images/F-16-image.png", cv.IMREAD_GRAYSCALE)

    n = 4
    bayer_matrix = generate_bayer_matrix(n)
    thresholds_matrix = generate_thresholds_matrix(bayer_matrix)
    output = Ordered_Dithering(img,thresholds_matrix)

    cv.imshow('Grayscale Image',output )


    cv.waitKey(0)  
    cv.destroyAllWindows()  # 關閉所有視窗
    # TODO:Show your picture


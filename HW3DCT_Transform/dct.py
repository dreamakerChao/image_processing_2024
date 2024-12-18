import sys
import cv2 as cv
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.fft import dct, idct

def calculate_psnr(original, reconstructed):
    mse = np.mean((original - reconstructed) ** 2)
    if mse == 0:
        return float('inf')
    max_pixel = 255.0
    psnr = 10 * np.log10((max_pixel ** 2) / mse)
    return psnr

def save_dct_as_image(dct_result, output_file):
    dct_visual = np.log(np.abs(dct_result) + 1)

    dct_visual = (dct_visual / np.max(dct_visual) * 255).astype(np.uint8)

    cv.imwrite(output_file, dct_visual)
    print(f"DCT saved: {output_file}")

def Global_DCT(img):
    # TODO:
        # 1. Use opencv’s DCT function or numpy’s fft function or Designed according to formula
        # EX: cv.dct(img) <--> cv.idct(img) 
    dct_x = dct(img, type=2, axis=0, norm='ortho')
    dct_xy = dct(dct_x, type=2, axis=1, norm='ortho')

    return dct_xy

def Local_DCT(img, kernel_size = 8):
    #TODO:
        # 1. Use opencv’s DCT function or numpy’s fft2 function / Designed according to formula
        # 2. Decide the core size by yourself (default 8 * 8)
    h, w = img.shape
    dct_result = np.zeros_like(img, dtype=np.float32)  

    for i in range(0, h, kernel_size):
        for j in range(0, w, kernel_size):

            block = img[i:i + kernel_size, j:j + kernel_size]

            padded_block = np.zeros((kernel_size, kernel_size), dtype=np.float32)
            padded_block[:block.shape[0], :block.shape[1]] = block

            dct_block = dct(dct(padded_block, type=2, axis=0, norm='ortho'), type=2, axis=1, norm='ortho')

            dct_result[i:i + block.shape[0], j:j + block.shape[1]] = dct_block[:block.shape[0], :block.shape[1]]

    return dct_result

def frequency_Domain_filter(DCT_img, crop_size=(150, 150)):
    # TODO:
        # 1. Input the DCT transform frequency domain image
        # 2. Crop areas of concentrated energy in the image
        # 3. After outputting the result, do IDCT
    IDCT_img = idct(idct(DCT_img, axis=1, norm='ortho'), axis=0, norm='ortho')
    cv.imwrite('./result/reconstructed_image_direct.png', np.clip(IDCT_img , 0, 255).astype(np.uint8))
    cropped_DCT = np.zeros_like(DCT_img)
    cropped_DCT[:crop_size[0], :crop_size[1]] = DCT_img[:crop_size[0], :crop_size[1]]

    # 逆 DCT 還原圖像
    IDCT_img = idct(idct(cropped_DCT, axis=1, norm='ortho'), axis=0, norm='ortho')
    return IDCT_img


def butterfly_dct_8(input_vector):

    assert len(input_vector) == 8, "Input vector must have a length of 8"
    
    # Stage 1: 加法與減法
    stage1 = np.zeros(8)
    stage1[0] = input_vector[0] + input_vector[7]
    stage1[1] = input_vector[1] + input_vector[6]
    stage1[2] = input_vector[2] + input_vector[5]
    stage1[3] = input_vector[3] + input_vector[4]
    stage1[4] = input_vector[3] - input_vector[4]
    stage1[5] = input_vector[2] - input_vector[5]
    stage1[6] = input_vector[1] - input_vector[6]
    stage1[7] = input_vector[0] - input_vector[7]
    
    # Stage 2: 係數運算 (cos/sin)
    c1 = np.cos(np.pi / 16)
    c3 = np.cos(3 * np.pi / 16)
    s1 = np.sin(np.pi / 16)
    s3 = np.sin(3 * np.pi / 16)

    stage2 = np.zeros(8)
    stage2[0] = stage1[0] + stage1[3]
    stage2[1] = stage1[1] + stage1[2]
    stage2[2] = c3 * stage1[4] + s3 * stage1[5]
    stage2[3] = c1 * stage1[6] + s1 * stage1[7]
    stage2[4] = stage1[0] - stage1[3]
    stage2[5] = stage1[1] - stage1[2]
    stage2[6] = -s3 * stage1[4] + c3 * stage1[5]
    stage2[7] = -s1 * stage1[6] + c1 * stage1[7]

    # Stage 3: \sqrt{2} 處理
    stage3 = np.zeros(8)
    stage3[0] = stage2[0]
    stage3[1] = stage2[1]
    stage3[2] = np.sqrt(2) * stage2[2]
    stage3[3] = np.sqrt(2) * stage2[3]
    stage3[4] = stage2[4]
    stage3[5] = stage2[5]
    stage3[6] = np.sqrt(2) * stage2[6]
    stage3[7] = np.sqrt(2) * stage2[7]

    return stage3

def dct_2d_butterfly(img):
    """
    使用蝶形結構計算圖像的 2D DCT
    :param img: 輸入灰階圖像
    :return: DCT 頻率域圖像
    """
    h, w = img.shape

    # 零填充到 8 的倍數
    padded_h = (h + 7) // 8 * 8
    padded_w = (w + 7) // 8 * 8
    padded_img = np.zeros((padded_h, padded_w), dtype=np.float32)
    padded_img[:h, :w] = img

    # 計算 2D DCT
    dct_result = np.zeros_like(padded_img, dtype=np.float32)

    # 對每一行進行 1D DCT
    for i in range(padded_h):
        for j in range(0, padded_w, 8):
            dct_result[i, j:j + 8] = butterfly_dct_8(padded_img[i, j:j + 8])

    # 對每一列進行 1D DCT
    final_result = np.zeros_like(padded_img, dtype=np.float32)
    for j in range(padded_w):
        for i in range(0, padded_h, 8):
            final_result[i:i + 8, j] = butterfly_dct_8(dct_result[i:i + 8, j])

    return final_result[:h, :w]  # 截取回原圖大小
 
if __name__ == '__main__':

    img = cv.imread("./images/Baboon-image.png", cv.IMREAD_GRAYSCALE)
    dct_result=Global_DCT(img)
    psnr1=calculate_psnr(img,dct_result)
    print(f"psnr:{psnr1}")
    save_dct_as_image(dct_result,"./result/dct_result.png")
    reconstructed_img = frequency_Domain_filter(dct_result, crop_size=(int(img.shape[0]/5), int(img.shape[1]/5)))
    psnr1=calculate_psnr(img,reconstructed_img)
    print(f"psnr:{psnr1}")

    dct_result=Global_DCT(reconstructed_img)
    save_dct_as_image(dct_result,"./result/dct_after_filter.png")
    cv.imwrite("./result/reconstructed_image.png", np.clip(reconstructed_img, 0, 255).astype(np.uint8))

    local_dct_result = Local_DCT(img, kernel_size=8)
    save_dct_as_image(local_dct_result,"./result/local_dct_result.png")
    reconstructed_img = frequency_Domain_filter(local_dct_result, crop_size=(int(img.shape[0]/5), int(img.shape[1]/5)))
    cv.imwrite("./result/local_reconstructed_image.png", np.clip(reconstructed_img, 0, 255).astype(np.uint8))
    psnr1=calculate_psnr(img,reconstructed_img)
    print(f"psnr:{psnr1}")

    local_dct_result =dct_2d_butterfly(img)
    save_dct_as_image(local_dct_result,"./result/local_dct_result_butterfly.png")
    reconstructed_img = frequency_Domain_filter(local_dct_result, crop_size=(int(img.shape[0]/5), int(img.shape[1]/5)))
    cv.imwrite("./result/butterfly_reconstructed_image.png", np.clip(reconstructed_img, 0, 255).astype(np.uint8))
    psnr1=calculate_psnr(img,reconstructed_img)
    print(f"psnr:{psnr1}")
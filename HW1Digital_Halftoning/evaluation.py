import halftoning as ht
import cv2 as cv
from concurrent.futures import ThreadPoolExecutor

def process_image(n, img, img2):
    bayer_matrix = ht.generate_bayer_matrix(n)
    thresholds_matrix = ht.generate_thresholds_matrix(bayer_matrix)

    output1 = ht.Ordered_Dithering(img, thresholds_matrix)
    output2 = ht.Ordered_Dithering(img2, thresholds_matrix)

    cv.imwrite(f'./HW1Digital_Halftoning/evaluation/F-16-image_ordered_{n}.png', output1)
    print(f"{n} F_16 PSNR: {ht.calculate_PSNR(img,output1)}")
    cv.imwrite(f'./HW1Digital_Halftoning/evaluation/Baboon-image_ordered_{n}.png', output2)
    print(F"{n} Baboon PSNR: {ht.calculate_PSNR(img2,output2)}")

if __name__ == "__main__":
    img = cv.imread("./HW1Digital_Halftoning/images/F-16-image.png", cv.IMREAD_GRAYSCALE)
    img2 = cv.imread("./HW1Digital_Halftoning/images/Baboon-image.png", cv.IMREAD_GRAYSCALE)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_image, n, img, img2) for n in range(2, 8)]
        for future in futures:
            future.result()

    print("done!")

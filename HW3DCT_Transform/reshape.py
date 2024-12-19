import cv2
import numpy as np

def resize_image_to_512(image_path, output_path):
    """
    Resize the input image to 512x512 and save the result.
    """
    # 讀取圖片
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Image not found.")
        return

    # 調整圖片大小到 512x512
    resized_image = cv2.resize(image, (512, 512), interpolation=cv2.INTER_AREA)

    # 儲存調整後的圖片
    cv2.imwrite(output_path, resized_image)
    print(f"Resized image saved to {output_path}")

    # 顯示圖片
    cv2.imshow("Resized Image (512x512)", resized_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 主程式
if __name__ == "__main__":
    # 設定輸入和輸出檔案路徑
    input_image_path = "./images/F-16-image.png"  # 替換為原始圖片路徑
    output_image_path = "resized_F-16-image.png"  # 輸出圖片路徑

    # 呼叫函數進行圖片調整
    resize_image_to_512(input_image_path, output_image_path)

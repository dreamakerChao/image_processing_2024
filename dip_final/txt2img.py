from PIL import Image
import numpy as np

# 讀取 txt 文件，假設文件名為 'data.txt'
with open('lena_blurred.txt', 'r') as file:
    data = []
    for line in file:
        row = list(map(int, line.split()))
        data.append(row)

# 將 data 轉換成 NumPy 陣列
data = np.array(data, dtype=np.uint8)

# 將 NumPy 陣列轉換為圖片
img = Image.fromarray(data, mode='L')  # 'L' 表示灰度模式

# 儲存圖片
img.save('output_imag_hls.png')

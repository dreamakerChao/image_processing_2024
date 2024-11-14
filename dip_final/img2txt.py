# 使用 Python 將圖像轉換為灰度數據並保存為 .txt 文件
from PIL import Image
import numpy as np

# 打開圖像並轉換為灰度
img = Image.open('./images/lena.png').convert('L')  # 'L' 表示灰度
img_resized = img.resize((60, 60))      # 可選，縮放到 256x256

# 將像素值轉換為數組並保存為文本
img_data = np.array(img_resized)
np.savetxt('./txt/lena_data.txt', img_data, fmt='%d')

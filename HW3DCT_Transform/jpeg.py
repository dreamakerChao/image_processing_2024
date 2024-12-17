import numpy as np
import cv2
import matplotlib.pyplot as plt

# JPEG 標準亮度量化表
base_quantization_table = np.array([
    [16, 11, 10, 16, 24, 40, 51, 61],
    [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56],
    [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 68, 109, 103, 77],
    [24, 35, 55, 64, 81, 104, 113, 92],
    [49, 64, 78, 87, 103, 121, 120, 101],
    [72, 92, 95, 98, 112, 100, 103, 99]
], dtype=np.float32)

def scale_quantization_table(base_table, scale_factor):
    """根據 Scale Factor 調整量化表."""
    scaled_table = np.round(base_table * scale_factor)
    scaled_table[scaled_table == 0] = 1  # 避免量化表出現 0
    return scaled_table

def dct_block(block):
    """對 8x8 區塊執行 DCT 轉換."""
    return cv2.dct(block.astype(np.float32))

def idct_block(block):
    """對 8x8 區塊執行反 DCT 轉換."""
    return cv2.idct(block)

def jpeg_compress(image, quant_table):
    """對影像進行 DCT 轉換和量化壓縮."""
    h, w = image.shape
    compressed = np.zeros((h, w), dtype=np.float32)
    for i in range(0, h, 8):
        for j in range(0, w, 8):
            block = image[i:i+8, j:j+8] - 128  # 中心化
            dct = dct_block(block)
            compressed[i:i+8, j:j+8] = np.round(dct / quant_table)  # 量化
    return compressed

def jpeg_decompress(compressed, quant_table):
    """對壓縮後的影像進行反量化和反 DCT."""
    h, w = compressed.shape
    reconstructed = np.zeros((h, w), dtype=np.float32)
    for i in range(0, h, 8):
        for j in range(0, w, 8):
            block = compressed[i:i+8, j:j+8] * quant_table  # 反量化
            idct = idct_block(block) + 128  # 反 DCT 並去中心化
            reconstructed[i:i+8, j:j+8] = np.clip(idct, 0, 255)
    return np.uint8(reconstructed)

# 讀取灰階影像
image = cv2.imread('./images/F-16-image.png', cv2.IMREAD_GRAYSCALE)
image = cv2.resize(image, (256, 256))  # 簡化處理

# 調整壓縮比例
scale_factor = 0.10  # 可調整：<1 (高品質)，>1 (高壓縮)
quantization_table = scale_quantization_table(base_quantization_table, scale_factor)

# 壓縮與還原影像
compressed = jpeg_compress(image, quantization_table)
reconstructed = jpeg_decompress(compressed, quantization_table)

# 顯示結果
plt.figure(figsize=(10, 5))
plt.subplot(1, 3, 1)
plt.title("Original Image")
plt.imshow(image, cmap='gray')

plt.subplot(1, 3, 2)
plt.title(f"Compressed (Scale Factor={scale_factor})")
plt.imshow(compressed, cmap='gray')

plt.subplot(1, 3, 3)
plt.title("Reconstructed Image")
plt.imshow(reconstructed, cmap='gray')

plt.tight_layout()
plt.show()

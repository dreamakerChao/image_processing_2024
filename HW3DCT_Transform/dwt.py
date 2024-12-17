import numpy as np
import cv2
import matplotlib.pyplot as plt

def haar_1d(signal):
    """1D Haar Wavelet Transform for one row or column."""
    n = len(signal)
    output = np.zeros_like(signal, dtype=np.float32)
    half = n // 2
    for i in range(half):
        output[i] = (signal[2 * i] + signal[2 * i + 1]) / np.sqrt(2)  # Low frequency
        output[half + i] = (signal[2 * i] - signal[2 * i + 1]) / np.sqrt(2)  # High frequency
    return output

def haar_2d(image):
    """2D Haar Wavelet Transform."""
    h, w = image.shape
    transformed = np.copy(image).astype(np.float32)
    
    # Step 1: Perform 1D transform on rows
    for i in range(h):
        transformed[i, :] = haar_1d(transformed[i, :])
    
    # Step 2: Perform 1D transform on columns
    for j in range(w):
        transformed[:, j] = haar_1d(transformed[:, j])
    
    return transformed

def dwt_3level(image):
    """3-Level 2D Haar Wavelet Transform."""
    # Level 1 transform
    level1 = haar_2d(image)
    h, w = image.shape
    LL1 = level1[:h//2, :w//2]
    LH1 = level1[:h//2, w//2:]
    HL1 = level1[h//2:, :w//2]
    HH1 = level1[h//2:, w//2:]

    # Level 2 transform on LL1
    level2 = haar_2d(LL1)
    LL2 = level2[:h//4, :w//4]
    LH2 = level2[:h//4, w//4:]
    HL2 = level2[h//4:, :w//4]
    HH2 = level2[h//4:, w//4:]

    # Level 3 transform on LL2
    level3 = haar_2d(LL2)
    LL3 = level3[:h//8, :w//8]
    LH3 = level3[:h//8, w//8:]
    HL3 = level3[h//8:, :w//8]
    HH3 = level3[h//8:, w//8:]

    return (LL1, LH1, HL1, HH1), (LL2, LH2, HL2, HH2), (LL3, LH3, HL3, HH3)

def combine_dwt_levels(level1, level2, level3):
    """Combine 3-level DWT into one large image."""
    # Unpack levels
    LL1, LH1, HL1, HH1 = level1
    LL2, LH2, HL2, HH2 = level2
    LL3, LH3, HL3, HH3 = level3

    # Create placeholders for the combined image
    h, w = LL1.shape[0] * 2, LL1.shape[1] * 2
    combined = np.zeros((h, w), dtype=np.float32)
    
    # Level 1 placement
    combined[:h//2, :w//2] = LL1
    combined[:h//2, w//2:] = LH1
    combined[h//2:, :w//2] = HL1
    combined[h//2:, w//2:] = HH1

    # Level 2 placement (inside LL1)
    combined[:h//4, :w//4] = LL2
    combined[:h//4, w//4:w//2] = LH2
    combined[h//4:h//2, :w//4] = HL2
    combined[h//4:h//2, w//4:w//2] = HH2

    # Level 3 placement (inside LL2)
    combined[:h//8, :w//8] = LL3
    combined[:h//8, w//8:w//4] = LH3
    combined[h//8:h//4, :w//8] = HL3
    combined[h//8:h//4, w//8:w//4] = HH3

    return combined


def inverse_haar_1d(low, high):
    """1D Inverse Haar Wavelet Transform for one row or column."""
    n = len(low) * 2
    output = np.zeros(n, dtype=np.float32)
    for i in range(len(low)):
        output[2 * i] = (low[i] + high[i]) / np.sqrt(2)    # Even index
        output[2 * i + 1] = (low[i] - high[i]) / np.sqrt(2)  # Odd index
    return output

def inverse_haar_2d(LL, LH, HL, HH):
    """2D Inverse Haar Wavelet Transform."""
    h, w = LL.shape  # LL is the low-low frequency subband
    restored = np.zeros((h * 2, w * 2), dtype=np.float32)

    # Step 1: Combine LL and LH (Vertical Inverse Transform)
    vertical = np.zeros((h * 2, w), dtype=np.float32)
    for i in range(w):
        low = LL[:, i]
        high = LH[:, i]
        vertical[:, i] = inverse_haar_1d(low, high)

    # Step 2: Combine HL and HH (Vertical Inverse Transform)
    for i in range(w):
        low = HL[:, i]
        high = HH[:, i]
        vertical[h:, i] = inverse_haar_1d(low, high)

    # Step 3: Horizontal Inverse Transform
    final_restored = np.zeros((h * 2, w * 2), dtype=np.float32)
    for i in range(h * 2):
        low = vertical[i, :w]
        high = vertical[i, w:]
        final_restored[i, :] = inverse_haar_1d(low, high)

    return final_restored

def reconstruct_3level(LL3, LH3, HL3, HH3, LH2, HL2, HH2, LH1, HL1, HH1):
    """Reconstruct the image from 3-Level DWT components."""
    # Level 3: Reconstruct LL2
    LL2 = inverse_haar_2d(LL3, LH3, HL3, HH3)

    # Level 2: Reconstruct LL1
    LL1 = inverse_haar_2d(LL2, LH2, HL2, HH2)

    # Level 1: Reconstruct full image
    restored_image = inverse_haar_2d(LL1, LH1, HL1, HH1)

    return restored_image

if __name__ == "__main__":
    # 讀取灰階影像
    image = cv2.imread('images/F-16-image.png', cv2.IMREAD_GRAYSCALE)
    image = cv2.resize(image, (256, 256))  # Resize for simplicity

    # 執行 3-Level DWT
    level1, level2, level3 = dwt_3level(image)

    # 拼接成一大張圖
    combined_image = combine_dwt_levels(level1, level2, level3)

    # 顯示結果
    plt.figure(figsize=(10, 10))
    plt.imshow(combined_image, cmap='gray')
    plt.title("3-Level DWT Combined Image")
    plt.axis('off')
    plt.show()

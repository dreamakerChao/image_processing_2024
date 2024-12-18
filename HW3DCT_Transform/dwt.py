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

def dwt_2level(image):
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

    return (LL1, LH1, HL1, HH1), (LL2, LH2, HL2, HH2)

def combine_dwt_levels_2level(level1, level2):
    """Combine 2-level DWT into one large image."""
    # Unpack levels
    LL1, LH1, HL1, HH1 = level1
    LL2, LH2, HL2, HH2 = level2

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

    return combined

def inverse_haar_1d(low, high):
    """1D Inverse Haar Wavelet Transform for one row or column."""
    if len(low) == 0 or len(high) == 0:
        raise ValueError("Input arrays 'low' and 'high' must not be empty.")
    
    n = len(low) * 2
    output = np.zeros(n, dtype=np.float32)
    for i in range(len(low)):
        output[2 * i] = (low[i] + high[i]) / np.sqrt(2)    # Even index
        output[2 * i + 1] = (low[i] - high[i]) / np.sqrt(2)  # Odd index
    return output

def inverse_haar_2d(LL, LH, HL, HH):
    """2D Inverse Haar Wavelet Transform."""
    if LL.shape != LH.shape or LL.shape != HL.shape or LL.shape != HH.shape:
        raise ValueError("All subbands must have the same shape.")

    h, w = LL.shape
    print(f"Input subbands shapes: LL={LL.shape}, LH={LH.shape}, HL={HL.shape}, HH={HH.shape}")

    # Combine LL and LH (Vertical Inverse Transform)
    vertical = np.zeros((h * 2, w), dtype=np.float32)
    for j in range(w):
        low = LL[:, j]
        high = LH[:, j]
        output = inverse_haar_1d(low, high)
        vertical[:h, j] = output[:h]
        vertical[h:, j] = output[h:]

    print(f"Vertical shape after transform: {vertical.shape}")

    # Combine HL and HH (Vertical Inverse Transform)
    for j in range(w):
        low = HL[:, j]
        high = HH[:, j]
        output = inverse_haar_1d(low, high)
        vertical[:h, j] += output[:h]
        vertical[h:, j] += output[h:]

    # Horizontal inverse transform
    final_restored = np.zeros((h * 2, w * 2), dtype=np.float32)
    for i in range(h * 2):
        low = vertical[i, :w]
        high = vertical[i, w:]
        final_restored[i, :] = inverse_haar_1d(low, high)

    print(f"Restored image shape: {final_restored.shape}")
    return final_restored


def reconstruct_2level(LL2, LH2, HL2, HH2, LH1, HL1, HH1):
    """Reconstruct the image from 2-Level DWT components."""
    # Level 2: Reconstruct LL1
    LL1 = inverse_haar_2d(LL2, LH2, HL2, HH2)

    # Level 1: Reconstruct full image
    restored_image = inverse_haar_2d(LL1, LH1, HL1, HH1)

    return restored_image


if __name__ == "__main__":
    # 讀取灰階影像
    image = cv2.imread('images/F-16-image.png', cv2.IMREAD_GRAYSCALE)
    image = cv2.resize(image, (256, 256))  # Resize for simplicity

    # 執行 2-Level DWT
    level1, level2 = dwt_2level(image)

    # 拼接成一大張圖
    combined_image = combine_dwt_levels_2level(level1, level2)

    # 顯示結果
    plt.figure(figsize=(10, 10))
    plt.imshow(combined_image, cmap='gray')
    plt.title("2-Level DWT Combined Image")
    plt.axis('off')
    plt.show()

    # 進行還原 (2-Level IDWT)
    restored_image = reconstruct_2level(
        level2[0], level2[1], level2[2], level2[3],  # 第二層
        level1[1], level1[2], level1[3]             # 第一層
    )

    # 顯示還原結果
    plt.figure(figsize=(10, 10))
    plt.imshow(restored_image, cmap='gray')
    plt.title("Reconstructed Image (2-Level IDWT)")
    plt.axis('off')
    plt.show()
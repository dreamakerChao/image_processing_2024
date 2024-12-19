import cv2
import numpy as np
import ctypes
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid QT plugin issues
import matplotlib.pyplot as plt

# Load the shared library
dwt = ctypes.CDLL('./libdwt.so')

# Define the updated C function interface for dwt_2d
dwt.dwt_2d.argtypes = [
    ctypes.c_int,  # Matrix size N
    ctypes.POINTER(ctypes.c_double),  # Input matrix pointer
    ctypes.POINTER(ctypes.c_double),  # LL output pointer
    ctypes.POINTER(ctypes.c_double),  # LH output pointer
    ctypes.POINTER(ctypes.c_double),  # HL output pointer
    ctypes.POINTER(ctypes.c_double)   # HH output pointer
]
dwt.dwt_2d.restype = None

# Define the updated C function interface for idwt_2d
dwt.idwt_2d.argtypes = [
    ctypes.c_int,  # Matrix size N
    ctypes.POINTER(ctypes.c_double),  # LL input pointer
    ctypes.POINTER(ctypes.c_double),  # LH input pointer
    ctypes.POINTER(ctypes.c_double),  # HL input pointer
    ctypes.POINTER(ctypes.c_double),  # HH input pointer
    ctypes.POINTER(ctypes.c_double)   # Reconstructed output pointer
]
dwt.idwt_2d.restype = None

def perform_dwt(image):
    """
    Perform 1-level DWT using the updated C shared library.
    """
    N = image.shape[0]
    size = N // 2

    # Allocate output arrays
    LL = np.zeros((size, size), dtype=np.float64)
    LH = np.zeros((size, size), dtype=np.float64)
    HL = np.zeros((size, size), dtype=np.float64)
    HH = np.zeros((size, size), dtype=np.float64)

    # Call the updated C function
    dwt.dwt_2d(
        N,
        image.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        LL.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        LH.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        HL.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        HH.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    )
    return LL, LH, HL, HH

def perform_idwt(LL, LH, HL, HH):
    """
    Perform inverse DWT using the updated C shared library.
    """
    size = LL.shape[0] * 2  # Reconstructed size
    reconstructed = np.zeros((size, size), dtype=np.float64)

    # Call the updated C function
    dwt.idwt_2d(
        size,
        LL.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        LH.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        HL.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        HH.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        reconstructed.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    )
    return reconstructed

def perform_2level_dwt(image):
    """
    Perform 2-level DWT by applying DWT twice on the LL coefficients.
    """
    # First-level DWT
    LL1, LH1, HL1, HH1 = perform_dwt(image)

    # Second-level DWT on LL1
    LL2, LH2, HL2, HH2 = perform_dwt(LL1)

    return LL2, LH2, HL2, HH2, LH1, HL1, HH1

def reconstruct_visualization(LL2, LH2, HL2, HH2, LH1, HL1, HH1):
    """
    Reconstruct the visualization by stacking the DWT components.
    """
    # Combine level 2 components
    level2_top = np.hstack((LL2, LH2))
    level2_bottom = np.hstack((HL2, HH2))
    level2 = np.vstack((level2_top, level2_bottom))

    # Combine level 1 components with level 2
    level1_top = np.hstack((level2, LH1))
    level1_bottom = np.hstack((HL1, HH1))
    combined = np.vstack((level1_top, level1_bottom))

    return combined

def main():
    # Load and preprocess the image
    image = cv2.imread('./images/F-16-image.png', cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("Error: Image not found.")
        return

    # Normalize the image
    resized_image = image.astype(np.float64) / 255.0

    # Perform 2-level DWT
    LL2, LH2, HL2, HH2, LH1, HL1, HH1 = perform_2level_dwt(resized_image)

    # Reconstruct visualization
    visualization = reconstruct_visualization(LL2, LH2, HL2, HH2, LH1, HL1, HH1)

    # Normalize the visualization for display
    visualization_normalized = cv2.normalize(visualization, None, 0, 255, cv2.NORM_MINMAX)
    visualization_normalized = visualization_normalized.astype(np.uint8)

    # Save the visualization to a file
    plt.figure(figsize=(10, 10))
    plt.imshow(visualization_normalized, cmap='gray')
    plt.title('2-Level DWT Visualization')
    plt.axis('off')
    plt.savefig('dwt_visualization.png', dpi=300)

    # Perform IDWT to reconstruct the original image
    reconstructed_image = perform_idwt(LL2, LH2, HL2, HH2)

    # Normalize the reconstructed image for display
    reconstructed_normalized = cv2.normalize(reconstructed_image, None, 0, 255, cv2.NORM_MINMAX)
    reconstructed_normalized = reconstructed_normalized.astype(np.uint8)

    # Save the reconstructed image to a file
    plt.figure(figsize=(10, 10))
    plt.imshow(reconstructed_normalized, cmap='gray')
    plt.title('Reconstructed Image')
    plt.axis('off')
    plt.savefig('reconstructed_image.png', dpi=300)

if __name__ == "__main__":
    main()

import ctypes
import numpy as np

# Load the shared library
jpeg = ctypes.CDLL('./libjpeg_image.so')

# Define the C function signature
jpeg.compress_image.argtypes = [
    np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS"),  # Image array
    ctypes.c_int,  # Width
    ctypes.c_int,  # Height
    np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS")     # Output compressed data
]
jpeg.compress_image.restype = None

def compress_image(image):
    """
    Compress an entire image using the C library.
    """
    height, width = image.shape
    compressed_size = (width // 8) * (height // 8) * 64
    compressed = np.zeros(compressed_size, dtype=np.int32)

    jpeg.compress_image(image.astype(np.float64), width, height, compressed)
    return compressed

# Example usage
image = np.random.randint(0, 256, (16, 16), dtype=np.uint8)  # Example 16x16 image
compressed_data = compress_image(image)

print("Compressed Data:")
print(compressed_data)

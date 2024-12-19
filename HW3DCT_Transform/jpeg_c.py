import numpy as np
import ctypes

# Load the JPEG shared library
jpeg = ctypes.CDLL('./libjpeg.so')

# Define the function interfaces
jpeg.jpeg_compress.argtypes = [
    ctypes.c_int,  # Matrix size N
    ctypes.POINTER(ctypes.c_double),  # Input image pointer
    ctypes.POINTER(ctypes.c_int),  # Output compressed data pointer
    ctypes.POINTER(ctypes.c_int)   # Size of compressed data
]
jpeg.jpeg_compress.restype = None

jpeg.jpeg_decompress.argtypes = [
    ctypes.c_int,  # Matrix size N
    ctypes.POINTER(ctypes.c_int),  # Input compressed data pointer
    ctypes.c_int,  # Size of compressed data
    ctypes.POINTER(ctypes.c_double)  # Output decompressed image pointer
]
jpeg.jpeg_decompress.restype = None

def jpeg_compress(image):
    """
    Compress an image using the JPEG shared library.
    """
    N = image.shape[0]
    compressed = np.zeros(N * N, dtype=np.int32)
    compressed_size = ctypes.c_int()

    # Call the shared library function
    jpeg.jpeg_compress(
        N,
        image.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        compressed.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
        ctypes.byref(compressed_size)
    )
    return compressed[:compressed_size.value]

def jpeg_decompress(compressed, N):
    """
    Decompress an image using the JPEG shared library.
    """
    decompressed = np.zeros((N, N), dtype=np.float64)

    # Call the shared library function
    jpeg.jpeg_decompress(
        N,
        compressed.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
        len(compressed),
        decompressed.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    )
    return decompressed

def main():
    # Example: Compress and decompress a 512x512 grayscale image
    image = np.random.rand(512, 512).astype(np.float64)

    # Compress the image
    compressed = jpeg_compress(image)
    print(f"Compressed data size: {len(compressed)}")

    # Decompress the image
    decompressed = jpeg_decompress(compressed, 512)
    print("Decompression completed.")

if __name__ == "__main__":
    main()

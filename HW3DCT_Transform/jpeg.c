#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "dwt.h"

// Quantization step size
#define QUANT_STEP 20

// Quantization function
void quantize(int N, double *input, int *output, double step) {
    for (int i = 0; i < N * N; i++) {
        output[i] = (int)(input[i] / step);
    }
}

// Inverse quantization function
void inverse_quantize(int N, int *input, double *output, double step) {
    for (int i = 0; i < N * N; i++) {
        output[i] = input[i] * step;
    }
}

// Exported function for Python to compress an image
void jpeg_compress(int N, double *input, int *output, int *output_size) {
    double output_ll[N * N / 4], output_lh[N * N / 4], output_hl[N * N / 4], output_hh[N * N / 4];
    int quantized_ll[N * N / 4];

    // Perform DWT
    dwt_2d(N, input, output_ll, output_lh, output_hl, output_hh);

    // Quantize LL coefficients
    quantize(N / 2, output_ll, quantized_ll, QUANT_STEP);

    // Run-Length Encode (placeholder for entropy encoding)
    int index = 0, count = 1;
    for (int i = 1; i < N * N / 4; i++) {
        if (quantized_ll[i] == quantized_ll[i - 1]) {
            count++;
        } else {
            output[index++] = count;
            output[index++] = quantized_ll[i - 1];
            count = 1;
        }
    }
    output[index++] = count;
    output[index++] = quantized_ll[N * N / 4 - 1];
    *output_size = index;
}

// Exported function for Python to decompress an image
void jpeg_decompress(int N, int *input, int input_size, double *output) {
    double reconstructed_ll[N * N / 4], output_lh[N * N / 4], output_hl[N * N / 4], output_hh[N * N / 4];
    int decoded_quantized[N * N / 4];
    double temp_ll[N * N / 4];

    // Decode RLE (placeholder for entropy decoding)
    int index = 0;
    for (int i = 0; i < input_size; i += 2) {
        for (int j = 0; j < input[i]; j++) {
            decoded_quantized[index++] = input[i + 1];
        }
    }

    // Inverse Quantize
    inverse_quantize(N / 2, decoded_quantized, temp_ll, QUANT_STEP);

    // Perform IDWT
    idwt_2d(N, temp_ll, output_lh, output_hl, output_hh, output);
}

#ifndef DWT_H
#define DWT_H

#include <stdlib.h>
#include <math.h>

// Function prototypes for DWT and IDWT

/**
 * Perform 2D Discrete Wavelet Transform (DWT).
 * 
 * @param N The size of the input matrix (NxN).
 * @param input Pointer to the input matrix (flattened as a 1D array).
 * @param output_ll Pointer to the LL sub-band (flattened as a 1D array).
 * @param output_lh Pointer to the LH sub-band (flattened as a 1D array).
 * @param output_hl Pointer to the HL sub-band (flattened as a 1D array).
 * @param output_hh Pointer to the HH sub-band (flattened as a 1D array).
 */
void dwt_2d(int N, double *input, double *output_ll, double *output_lh, double *output_hl, double *output_hh);

/**
 * Perform 2D Inverse Discrete Wavelet Transform (IDWT).
 * 
 * @param N The size of the output matrix (NxN).
 * @param input_ll Pointer to the LL sub-band (flattened as a 1D array).
 * @param input_lh Pointer to the LH sub-band (flattened as a 1D array).
 * @param input_hl Pointer to the HL sub-band (flattened as a 1D array).
 * @param input_hh Pointer to the HH sub-band (flattened as a 1D array).
 * @param reconstructed Pointer to the reconstructed output matrix (flattened as a 1D array).
 */
void idwt_2d(int N, double *input_ll, double *input_lh, double *input_hl, double *input_hh, double *reconstructed);

#endif // DWT_H

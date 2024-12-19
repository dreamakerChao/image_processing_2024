#include <stdio.h>
#include <stdlib.h>

void dwt_2d(int N, double *input, double *output_ll, double *output_lh, double *output_hl, double *output_hh) {
    int halfN = N / 2;

    // Allocate temporary arrays for row-wise transform
    double *temp_low = (double *)malloc(N * halfN * sizeof(double));
    double *temp_high = (double *)malloc(N * halfN * sizeof(double));

    // Row-wise transform
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < halfN; j++) {
            int row_offset = i * N;
            temp_low[i * halfN + j] = 0.70710678118 * input[row_offset + 2 * j] + 0.70710678118 * input[row_offset + 2 * j + 1];
            temp_high[i * halfN + j] = 0.70710678118 * input[row_offset + 2 * j] - 0.70710678118 * input[row_offset + 2 * j + 1];
        }
    }

    // Column-wise transform
    for (int j = 0; j < halfN; j++) {
        for (int i = 0; i < halfN; i++) {
            int col_offset_low = 2 * i * halfN + j;
            int col_offset_high = (2 * i + 1) * halfN + j;

            output_ll[i * halfN + j] = 0.70710678118 * temp_low[col_offset_low] + 0.70710678118 * temp_low[col_offset_high];
            output_lh[i * halfN + j] = 0.70710678118 * temp_low[col_offset_low] - 0.70710678118 * temp_low[col_offset_high];
            output_hl[i * halfN + j] = 0.70710678118 * temp_high[col_offset_low] + 0.70710678118 * temp_high[col_offset_high];
            output_hh[i * halfN + j] = 0.70710678118 * temp_high[col_offset_low] - 0.70710678118 * temp_high[col_offset_high];
        }
    }

    // Free temporary arrays
    free(temp_low);
    free(temp_high);
}


void idwt_2d(int N, double *input_ll, double *input_lh, double *input_hl, double *input_hh, double *reconstructed) {
    int halfN = N / 2;

    // Allocate temporary arrays for row-wise inverse transform
    double *temp_low = (double *)malloc(N * halfN * sizeof(double));
    double *temp_high = (double *)malloc(N * halfN * sizeof(double));

    // Column-wise inverse transform
    for (int j = 0; j < halfN; j++) {
        for (int i = 0; i < halfN; i++) {
            int index_ll = i * halfN + j;
            int index_lh = i * halfN + j;
            int index_hl = i * halfN + j;
            int index_hh = i * halfN + j;

            temp_low[2 * i * halfN + j] = (input_ll[index_ll] + input_lh[index_lh]) * 0.70710678118;
            temp_low[(2 * i + 1) * halfN + j] = (input_ll[index_ll] - input_lh[index_lh]) * 0.70710678118;
            temp_high[2 * i * halfN + j] = (input_hl[index_hl] + input_hh[index_hh]) * 0.70710678118;
            temp_high[(2 * i + 1) * halfN + j] = (input_hl[index_hl] - input_hh[index_hh]) * 0.70710678118;
        }
    }

    // Row-wise inverse transform
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < halfN; j++) {
            int temp_low_index = i * halfN + j;
            int temp_high_index = i * halfN + j;

            reconstructed[i * N + 2 * j] = (temp_low[temp_low_index] + temp_high[temp_high_index]) * 0.70710678118;
            reconstructed[i * N + 2 * j + 1] = (temp_low[temp_low_index] - temp_high[temp_high_index]) * 0.70710678118;
        }
    }

    // Free temporary arrays
    free(temp_low);
    free(temp_high);
}
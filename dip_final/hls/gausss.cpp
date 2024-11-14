#include <hls_stream.h>
#include <ap_int.h>
#include <ap_fixed.h>

typedef ap_uint<8> pixel_t; // 8-bit pixel type

void gaussian_blur(pixel_t img_in[60][60], pixel_t img_out[60][60]) {
    // Kernel values in Q8.8 format
    const ap_ufixed<12,4> kernel[5][5] = {
        0.003, 0.014, 0.022, 0.014, 0.003,
        0.014, 0.061, 0.101, 0.061, 0.014,
        0.022, 0.101, 0.166, 0.101, 0.022,
        0.014, 0.061, 0.101, 0.061, 0.014,
        0.003, 0.014, 0.022, 0.014, 0.003
    };

    for (int i = 2; i < 58; i++) {
        for (int j = 2; j < 58; j++) {
            ap_ufixed<12,8> sum[25];
            ap_ufixed<12,8> result = 0;
            int n = 0;

            // 1 Pipeline: Kernel Operation
            kernel_operation:
            for (int ki = -2; ki <= 2; ki++) {
                #pragma HLS PIPELINE II=1
                for (int kj = -2; kj <= 2; kj++) {
                    #pragma HLS UNROLL
                    sum[n++] = ap_ufixed<12,8>(img_in[i + ki][j + kj]) * kernel[ki + 2][kj + 2];
                }
            }

            // 2 Pipeline: Sumup Operation
            sumup_operation:
            #pragma HLS PIPELINE II=1
            for (int idx = 0; idx < 25; idx++) {
                #pragma HLS UNROLL
                result += sum[idx];
            }

            img_out[i][j] = ap_uint<8>(result + ap_ufixed<12,8>(0.5)); // round
        }
    }
}

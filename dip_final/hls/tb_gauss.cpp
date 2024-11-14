#include <iostream>
#include <fstream>
#include <ap_int.h>

#include "gausss.h"

typedef ap_uint<8> pixel_t;
pixel_t img_in[60][60];
pixel_t img_out[60][60];


int main() {

    std::ifstream infile("E:\\project\\HLS\\gauss\\lena_data.txt");
    if (!infile) {
        std::cerr << "Error opening file\n";
        return 1;
    }

    for (int i = 0; i < 60; i++) {
        for (int j = 0; j < 60; j++) {
            int pixel_value;
            std::cout << pixel_value << ' ';
            infile >> pixel_value;
            img_in[i][j] = static_cast<pixel_t>(pixel_value);
        }
    }
    infile.close();


    gaussian_blur(img_in, img_out);


    std::ofstream outfile("lena_blurred.txt");
    for (int i = 0; i < 60; i++) {
        for (int j = 0; j < 60; j++) {
            outfile << img_out[i][j] << " ";
            std::cout << img_out[i][j] << ' ';
        }
        outfile << "\n";
    }
    outfile.close();

    std::cout << "Gaussian Blur applied and saved to 'lena_blurred.txt'\n";
    return 0;
}

#define _USE_MATH_DEFINES
#include <math.h>

#include <stdio.h>
#include <stdlib.h>

#include <png.h>


#define PI 3.141592654153

void generate_gaussian_kernel(int size, double sigma, double kernel[size][size]) {
    int center = size / 2;
    double sum = 0.0;

    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            int x = i - center;
            int y = j - center;
            kernel[i][j] = (1.0 / (2.0 * PI * sigma * sigma)) * exp(-(x * x + y * y) / (2 * sigma * sigma));
            sum += kernel[i][j];
        }
    }

    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            kernel[i][j] /= sum;
        }
    }
}


void write_png_file(const char *filename, int width, int height, png_bytep *row_pointers) {
    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        perror("File could not be opened for writing");
        exit(EXIT_FAILURE);
    }

    png_structp png = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
    png_infop info = png_create_info_struct(png);
    if (setjmp(png_jmpbuf(png))) abort();

    png_init_io(png, fp);

    png_set_IHDR(
        png,
        info,
        width, height,
        8, // bit depth
        PNG_COLOR_TYPE_RGB, // RGB only, no alpha
        PNG_INTERLACE_NONE,
        PNG_COMPRESSION_TYPE_DEFAULT,
        PNG_FILTER_TYPE_DEFAULT
    );

    png_write_info(png, info);
    png_write_image(png, row_pointers);
    png_write_end(png, NULL);

    fclose(fp);
    png_destroy_write_struct(&png, &info);
}

void apply_gaussian_blur(int width, int height, png_bytep *row_pointers, int kernel_size, const double kernel[kernel_size][kernel_size]) {
    int offset = kernel_size / 2;
    png_bytep *copy = (png_bytep*)malloc(sizeof(png_bytep) * height);

    for (int y = 0; y < height; y++) {
        copy[y] = (png_byte*)malloc(width * 3); // 3 channels (RGB)
        for (int x = 0; x < width * 3; x++) {
            copy[y][x] = row_pointers[y][x];
        }
    }

    
    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            double r = 0, g = 0, b = 0;

            for (int ky = -offset; ky <= offset; ky++) {
                for (int kx = -offset; kx <= offset; kx++) {
                    int pixel_y = y + ky;
                    int pixel_x = x + kx;

                    if (pixel_y < 0 || pixel_y >= height || pixel_x < 0 || pixel_x >= width) {
                        continue;
                    }

                    png_bytep pixel = copy[pixel_y] + (pixel_x * 3); 

                    r += pixel[0] * kernel[ky + offset][kx + offset];
                    g += pixel[1] * kernel[ky + offset][kx + offset];
                    b += pixel[2] * kernel[ky + offset][kx + offset];
                }
            }

            png_bytep current_pixel = row_pointers[y] + (x * 3);
            current_pixel[0] = (png_byte)(r > 255.0 ? 255.0 : (r < 0.0 ? 0 : r));
            current_pixel[1] = (png_byte)(g > 255.0 ? 255.0 : (g < 0.0 ? 0 : g));
            current_pixel[2] = (png_byte)(b > 255.0 ? 255.0 : (b < 0.0 ? 0 : b));
        }
    }

    for (int y = 0; y < height; y++) {
        free(copy[y]);
    }
    free(copy);
}

void read_png_file(const char *filename, int *width, int *height, png_bytep **row_pointers) {
    FILE *fp = fopen(filename, "rb");
    if (!fp) {
        perror("File could not be opened");
        exit(EXIT_FAILURE);
    }

    png_structp png = png_create_read_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
    png_infop info = png_create_info_struct(png);
    if (setjmp(png_jmpbuf(png))) abort();

    png_init_io(png, fp);
    png_read_info(png, info);

    *width = png_get_image_width(png, info);
    *height = png_get_image_height(png, info);

    png_byte color_type = png_get_color_type(png, info);
    png_byte bit_depth = png_get_bit_depth(png, info);


    if (bit_depth == 16) png_set_strip_16(png);
    if (color_type == PNG_COLOR_TYPE_PALETTE) png_set_palette_to_rgb(png);
    if (color_type == PNG_COLOR_TYPE_GRAY || color_type == PNG_COLOR_TYPE_GRAY_ALPHA) png_set_gray_to_rgb(png);
    if (color_type & PNG_COLOR_MASK_ALPHA) png_set_strip_alpha(png);

    png_read_update_info(png, info);

    *row_pointers = (png_bytep*)malloc(sizeof(png_bytep) * (*height));
    for (int y = 0; y < *height; y++) {
        (*row_pointers)[y] = (png_byte*)malloc(png_get_rowbytes(png, info));
    }

    png_read_image(png, *row_pointers);
    fclose(fp);
    png_destroy_read_struct(&png, &info, NULL);
}

int main() {
    int size = 9;
    double sigma = 10;
    double kernel[size][size];

    generate_gaussian_kernel(size, sigma, kernel);

    printf("Gaussian Kernel (size = %d, sigma = %.2f):\n", size, sigma);
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            printf("%0.5f ", kernel[i][j]);
        }
        printf("\n");
    }

    int width, height;
    png_bytep *row_pointers = NULL;

    read_png_file("./images/Lena.png", &width, &height, &row_pointers);
    printf("Image Width: %d\n", width);
    printf("Image Height: %d\n", height);

    apply_gaussian_blur(width,height,row_pointers,size,kernel);
    write_png_file("./output_img/result.png", width, height, row_pointers);

    for (int y = 0; y < height; y++) {
        free(row_pointers[y]);
    }
    free(row_pointers);

    printf("Press Enter to continue...");
    getchar();
    return 0;
}

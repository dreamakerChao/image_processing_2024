#include <stdio.h>
#include <stdlib.h>
#include <png.h>

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

int main() {
    int width, height;
    png_bytep *row_pointers;

    read_png_file("./images/Lena.png", &width, &height, &row_pointers);

    write_png_file("./output_img/Lena_output.png", width, height, row_pointers);

    for (int y = 0; y < height; y++) {
        free(row_pointers[y]);
    }
    free(row_pointers);

    return 0;
}

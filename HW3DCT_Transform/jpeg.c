#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#define BLOCK_SIZE 8 // 8x8 block size

typedef struct HuffmanNode {
    int symbol;         // (zero_count, value)
    int frequency;      // freq
    struct HuffmanNode *left;
    struct HuffmanNode *right;
} HuffmanNode;

typedef struct PriorityQueueNode {
    HuffmanNode *node;
    struct PriorityQueueNode *next;
} PriorityQueueNode;

// Zig-Zag scan order
int zigzag_order[BLOCK_SIZE * BLOCK_SIZE] = {
    0,  1,  5,  6, 14, 15, 27, 28,
    2,  4,  7, 13, 16, 26, 29, 42,
    3,  8, 12, 17, 25, 30, 41, 43,
    9, 11, 18, 24, 31, 40, 44, 53,
    10, 19, 23, 32, 39, 45, 52, 54,
    20, 22, 33, 38, 46, 51, 55, 60,
    21, 34, 37, 47, 50, 56, 59, 61,
    35, 36, 48, 49, 57, 58, 62, 63
};

// Quantization table
int quant_table[BLOCK_SIZE][BLOCK_SIZE] = {
    {16, 11, 10, 16, 24, 40, 51, 61},
    {12, 12, 14, 19, 26, 58, 60, 55},
    {14, 13, 16, 24, 40, 57, 69, 56},
    {14, 17, 22, 29, 51, 87, 80, 62},
    {18, 22, 37, 56, 68, 109, 103, 77},
    {24, 35, 55, 64, 81, 104, 113, 92},
    {49, 64, 78, 87, 103, 121, 120, 101},
    {72, 92, 95, 98, 112, 100, 103, 99}
};

// Fast DCT for 1D
void fast_dct_1d(double *data) {
    double tmp[8];
    double c1 = 0.9807852804032304, s1 = 0.19509032201612825;
    double c3 = 0.8314696123025452, s3 = 0.5555702330196022;
    double sqrt2 = 1.4142135623730951;

    tmp[0] = data[0] + data[7];
    tmp[7] = data[0] - data[7];
    tmp[1] = data[1] + data[6];
    tmp[6] = data[1] - data[6];
    tmp[2] = data[2] + data[5];
    tmp[5] = data[2] - data[5];
    tmp[3] = data[3] + data[4];
    tmp[4] = data[3] - data[4];

    double t0 = tmp[0] + tmp[3];
    double t3 = tmp[0] - tmp[3];
    double t1 = tmp[1] + tmp[2];
    double t2 = tmp[1] - tmp[2];
    tmp[0] = t0;
    tmp[1] = t1;
    tmp[2] = t2 * c1 + t3 * s1;
    tmp[3] = -t2 * s1 + t3 * c1;

    double t4 = tmp[4] * c3 + tmp[7] * s3;
    double t7 = -tmp[4] * s3 + tmp[7] * c3;
    double t5 = tmp[5] * c1 + tmp[6] * s1;
    double t6 = -tmp[5] * s1 + tmp[6] * c1;
    tmp[4] = t4;
    tmp[5] = t5;
    tmp[6] = t6;
    tmp[7] = t7;

    tmp[2] *= sqrt2;
    tmp[3] *= sqrt2;

    for (int i = 0; i < 8; i++) {
        data[i] = tmp[i];
    }
}

// Perform 2D DCT
void fast_dct_2d(double input[BLOCK_SIZE][BLOCK_SIZE], double output[BLOCK_SIZE][BLOCK_SIZE]) {
    double temp[BLOCK_SIZE][BLOCK_SIZE];

    for (int i = 0; i < BLOCK_SIZE; i++) {
        fast_dct_1d(input[i]);
        for (int j = 0; j < BLOCK_SIZE; j++) {
            temp[i][j] = input[i][j];
        }
    }

    for (int j = 0; j < BLOCK_SIZE; j++) {
        double column[BLOCK_SIZE];
        for (int i = 0; i < BLOCK_SIZE; i++) {
            column[i] = temp[i][j];
        }
        fast_dct_1d(column);
        for (int i = 0; i < BLOCK_SIZE; i++) {
            output[i][j] = column[i];
        }
    }
}

// Quantization
void quantize(double input[BLOCK_SIZE][BLOCK_SIZE], int output[BLOCK_SIZE][BLOCK_SIZE]) {
    for (int i = 0; i < BLOCK_SIZE; i++) {
        for (int j = 0; j < BLOCK_SIZE; j++) {
            output[i][j] = (int)round(input[i][j] / quant_table[i][j]);
        }
    }
}

// Zig-Zag scan
void zigzag_scan(int input[BLOCK_SIZE][BLOCK_SIZE], int output[BLOCK_SIZE * BLOCK_SIZE]) {
    for (int i = 0; i < BLOCK_SIZE * BLOCK_SIZE; i++) {
        output[zigzag_order[i]] = input[i/BLOCK_SIZE][i%BLOCK_SIZE];
    }
}

// RLE encoding
int rle_encode(int *input, int size, int *output) {
    int count = 0;
    int output_index = 0;

    for (int i = 0; i < size; i++) {
        if (input[i] == 0) {
            count++;
        } else {
            output[output_index++] = count;  // Number of zeros
            output[output_index++] = input[i];  // Non-zero value
            count = 0;  // Reset zero counter
        }
    }

    // Append end-of-block marker (if necessary)
    output[output_index++] = 0;  // Zero count
    output[output_index++] = 0;  // End marker

    return output_index;  // Return the size of the RLE-encoded output
}


PriorityQueueNode* enqueue(PriorityQueueNode *head, HuffmanNode *node) {
    PriorityQueueNode *new_node = (PriorityQueueNode*)malloc(sizeof(PriorityQueueNode));
    new_node->node = node;
    new_node->next = NULL;

    if (!head || node->frequency < head->node->frequency) {
        new_node->next = head;
        return new_node;
    }

    PriorityQueueNode *current = head;
    while (current->next && current->next->node->frequency <= node->frequency) {
        current = current->next;
    }
    new_node->next = current->next;
    current->next = new_node;
    return head;
}

HuffmanNode* dequeue(PriorityQueueNode **head) {
    if (!(*head)) return NULL;
    PriorityQueueNode *temp = *head;
    HuffmanNode *node = temp->node;
    *head = (*head)->next;
    free(temp);
    return node;
}

HuffmanNode* build_huffman_tree(int *symbols, int *frequencies, int size) {
    PriorityQueueNode *queue = NULL;

    for (int i = 0; i < size; i++) {
        HuffmanNode *node = (HuffmanNode*)malloc(sizeof(HuffmanNode));
        node->symbol = symbols[i];
        node->frequency = frequencies[i];
        node->left = NULL;
        node->right = NULL;
        queue = enqueue(queue, node);
    }

    while (queue && queue->next) {
        HuffmanNode *left = dequeue(&queue);
        HuffmanNode *right = dequeue(&queue);

        HuffmanNode *new_node = (HuffmanNode*)malloc(sizeof(HuffmanNode));
        new_node->symbol = -1; 
        new_node->frequency = left->frequency + right->frequency;
        new_node->left = left;
        new_node->right = right;
        queue = enqueue(queue, new_node);
    }

    return dequeue(&queue); 
}

void generate_huffman_codes(HuffmanNode *root, char **codes, char *current_code, int depth) {
    if (!root) return;

    if (root->left == NULL && root->right == NULL) {
        current_code[depth] = '\0';
        codes[root->symbol] = strdup(current_code);
        return;
    }

    current_code[depth] = '0';
    generate_huffman_codes(root->left, codes, current_code, depth + 1);

    current_code[depth] = '1';
    generate_huffman_codes(root->right, codes, current_code, depth + 1);
}

int compress_block_with_huffman(double input[BLOCK_SIZE][BLOCK_SIZE]) {
    double dct_block[BLOCK_SIZE][BLOCK_SIZE];
    int quantized_block[BLOCK_SIZE][BLOCK_SIZE];
    int zigzagged_block[BLOCK_SIZE * BLOCK_SIZE];
    int rle_output[BLOCK_SIZE * BLOCK_SIZE * 2];

    fast_dct_2d(input, dct_block);
    quantize(dct_block, quantized_block);
    zigzag_scan(quantized_block, zigzagged_block);
    int rle_size = rle_encode(zigzagged_block, BLOCK_SIZE * BLOCK_SIZE, rle_output);

    printf("RLE Result:\n");
    for (int i = 0; i < rle_size; i += 2) {
        printf("(%d, %d) ", rle_output[i], rle_output[i + 1]);
    }
    printf("\n");

    int symbols[BLOCK_SIZE * BLOCK_SIZE] = {0};
    int frequencies[BLOCK_SIZE * BLOCK_SIZE] = {0};
    int symbol_count = 0;

    for (int i = 0; i < rle_size; i += 2) {
        int symbol = (rle_output[i] << 8) | (rle_output[i + 1] & 0xFF);
        int found = 0;
        for (int j = 0; j < symbol_count; j++) {
            if (symbols[j] == symbol) {
                frequencies[j]++;
                found = 1;
                break;
            }
        }
        if (!found) {
            symbols[symbol_count] = symbol;
            frequencies[symbol_count] = 1;
            symbol_count++;
        }
    }
    HuffmanNode *root = build_huffman_tree(symbols, frequencies, symbol_count);
    char *codes[BLOCK_SIZE * BLOCK_SIZE] = {0};
    char current_code[BLOCK_SIZE * BLOCK_SIZE];
    generate_huffman_codes(root, codes, current_code, 0);


    printf("Huffman Codes:\n");
    for (int i = 0; i < symbol_count; i++) {
        printf("Symbol %d: %s\n", symbols[i], codes[symbols[i]]);
    }
    printf("\nHuffman Encoded Data:\n");
    for (int i = 0; i < rle_size; i += 2) {
        int symbol = (rle_output[i] << 8) | (rle_output[i + 1] & 0xFF);
        printf("%s ", codes[symbol]);
    }
    printf("\n");

    return 0;
}


// Compress a single 8x8 block
int compress_block(double input[BLOCK_SIZE][BLOCK_SIZE], int *output) {
    double dct_block[BLOCK_SIZE][BLOCK_SIZE];
    int quantized_block[BLOCK_SIZE][BLOCK_SIZE];
    int zigzagged_block[BLOCK_SIZE * BLOCK_SIZE];
    int rle_output[BLOCK_SIZE * BLOCK_SIZE * 2];  // 最大可能大小

    // DCT
    fast_dct_2d(input, dct_block);

    // Quantization
    quantize(dct_block, quantized_block);

    // Zig-Zag
    zigzag_scan(quantized_block, zigzagged_block);

    // RLE
    int rle_size = rle_encode(zigzagged_block, BLOCK_SIZE * BLOCK_SIZE, rle_output);

    printf("gg/n");
    int symbols[BLOCK_SIZE * BLOCK_SIZE] = {0};
    int frequencies[BLOCK_SIZE * BLOCK_SIZE] = {0};
    int symbol_count = 0;

    for (int i = 0; i < rle_size; i += 2) {
        int symbol = (rle_output[i] << 8) | (rle_output[i + 1] & 0xFF);
        int found = 0;
        for (int j = 0; j < symbol_count; j++) {
            if (symbols[j] == symbol) {
                frequencies[j]++;
                found = 1;
                break;
            }
        }
        if (!found) {
            symbols[symbol_count] = symbol;
            frequencies[symbol_count] = 1;
            symbol_count++;
        }
    }

    HuffmanNode *root = build_huffman_tree(symbols, frequencies, symbol_count);
    char *codes[BLOCK_SIZE * BLOCK_SIZE] = {0};
    char current_code[BLOCK_SIZE * BLOCK_SIZE];
    generate_huffman_codes(root, codes, current_code, 0);

    printf("Huffman Encoded Data:\n");
    for (int i = 0; i < rle_size; i += 2) {
        int symbol = (rle_output[i] << 8) | (rle_output[i + 1] & 0xFF);
        printf("%s ", codes[symbol]);
    }
    printf("\n");

    return rle_size;
}




// Main function for testing
int main() {
    double input_block[BLOCK_SIZE][BLOCK_SIZE] = {
        {52, 55, 61, 59, 79, 61, 76, 61},
        {62, 59, 55, 104, 94, 85, 59, 71},
        {63, 65, 66, 113, 144, 104, 63, 72},
        {64, 70, 70, 126, 154, 109, 71, 69},
        {67, 73, 68, 106, 122, 88, 68, 68},
        {68, 79, 60, 70, 77, 66, 58, 75},
        {69, 85, 64, 58, 55, 61, 65, 83},
        {70, 87, 69, 68, 65, 73, 78, 90}
    };

    int compressed[BLOCK_SIZE * BLOCK_SIZE * 2];  // Max possible size
    compress_block(input_block, compressed);

    return 0;
}

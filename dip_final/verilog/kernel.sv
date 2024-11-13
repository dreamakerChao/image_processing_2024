module kernel (
    input logic [71:0] pixel_batch, // 9 x 8 bit to 16-bit Q8.8
    output logic [7:0] result // 0-255
);
    logic [15:0] temp [8:0];
    logic [15:0] sum1, sum2, sum3, sum4, sum_final;




    q8_8_alu uut0 (.a({pixel_batch[7:0],8'd0}), .b(16'h001c), .result(temp[0]));
    q8_8_alu uut1 (.a({pixel_batch[15:8],8'd0}), .b(16'h001c), .result(temp[1]));
    q8_8_alu uut2 (.a({pixel_batch[23:16],8'd0}), .b(16'h001c), .result(temp[2]));
    q8_8_alu uut3 (.a({pixel_batch[31:24],8'd0}), .b(16'h001c), .result(temp[3]));
    q8_8_alu uut4 (.a({pixel_batch[39:32],8'd0}), .b(16'h001d), .result(temp[4]));
    q8_8_alu uut5 (.a({pixel_batch[47:40],8'd0}), .b(16'h001c), .result(temp[5]));
    q8_8_alu uut6 (.a({pixel_batch[55:48],8'd0}), .b(16'h001c), .result(temp[6]));
    q8_8_alu uut7 (.a({pixel_batch[63:56],8'd0}), .b(16'h001c), .result(temp[7]));
    q8_8_alu uut8 (.a({pixel_batch[71:64],8'd0}), .b(16'h001c), .result(temp[8]));

    always_comb begin : adding
        sum1 = temp[0] + temp[1];
        sum2 = temp[2] + temp[3];
        sum3 = temp[4] + temp[5];
        sum4 = temp[6] + temp[7];

        sum_final = sum1 + sum2 + sum3 + sum4 + temp[8];
        result = sum_final[15:8];
    end
endmodule

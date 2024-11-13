module q8_8_alu (
    input signed [15:0] a, // Q8.8
    input signed [15:0] b, // Q8.8
    output reg signed [15:0] result // Q8.8
);
    reg signed [31:0] full_product;

    always @(*) begin
        full_product = a * b; // Q16.16
        result = full_product[23:8]; // right shift 8 
    end
endmodule

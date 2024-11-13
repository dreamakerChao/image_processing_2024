module tb_q8_16_alu;
    reg signed [23:0] a;
    reg signed [23:0] b;
    reg [1:0] aluop;
    wire signed [23:0] result;

    q8_16_alu uut (
        .a(a),
        .b(b),
        .aluop(aluop),
        .result(result)
    );

    function real q8_16_to_real;
        input signed [23:0] fixed;
        begin
            q8_16_to_real = fixed / 65536.0; // 2^16 = 65536
        end
    endfunction

    // sim
    initial begin
        a = 24'h100000; // Q8.16   1.0
        b = 24'h800000;  // Q8.16   0.5

        // test add
        aluop = 2'b00;
        #10;
        $display("add: %f * %f , result = %f", q8_16_to_real(a), q8_16_to_real(b),q8_16_to_real(result));

        // test sub
        aluop = 2'b01;
        #10;
        $display("sub: %f * %f , result = %f", q8_16_to_real(a), q8_16_to_real(b),q8_16_to_real(result));

        // test multi
        aluop = 2'b10;
        #10;
        $display("Multiply: %f * %f, result = %f", q8_16_to_real(a), q8_16_to_real(b),q8_16_to_real(result));

        // test div
        aluop = 2'b11;
        #10;
        $display("div: %f * %f , result = %f", q8_16_to_real(a), q8_16_to_real(b),q8_16_to_real(result));

        // test div by 0
        b = 24'd0;
        aluop = 2'b11;
        #10;
        $display("div: %f * %f , result = %f", q8_16_to_real(a), q8_16_to_real(b),q8_16_to_real(result));

        $stop;
    end

endmodule

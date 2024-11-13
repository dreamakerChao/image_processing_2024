module image_rom (
    input wire clk,
    input wire [15:0] addr,
    output reg [7:0] pixel_out
);
    reg [7:0] rom [0:65535];

    initial begin
        $readmemh("image_data.txt", rom);
    end

    always @(posedge clk) begin
        pixel_out <= rom[addr];
    end
endmodule

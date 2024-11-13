module gaussian_blur (
    input wire clk,
    input wire rst_n, 
    input wire [23:0] s_axis_tdata,
    input wire s_axis_tvalid,
    input wire m_axis_tready
    
    output reg s_axis_tready,
    output reg [23:0] m_axis_tdata,
    output reg m_axis_tvalid,
    
);

    localparam  IDLE = 2'b00,
                DATA_FETCH = 2'b01,
                OPERATION = 2'b10,
                DONE = 2'b11;

    reg [1:0]state,state_next;

    reg [71:0] pixel_batch [2:0];
    reg [3:0] pixel_count;
    reg [7:0] result_r, result_g, result_b;


    kernel kr (.pixel_batch(pixel_batch[0]), .result(result_r));
    kernel kg (.pixel_batch(pixel_batch[1]), .result(result_g));
    kernel kb (.pixel_batch(pixel_batch[2]), .result(result_b));



    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
        end else begin
            state <= state_next;
        end
    end

    always_comb begin
        case (state)
            IDLE: begin
                if (s_axis_tvalid) begin
                    state_next = DATA_FETCH;
                end else begin
                    state_next = IDLE;
                end
            end

            DATA_FETCH: begin
                if (pixel_count == 4'd8) begin
                    state_next = OPERATION;
                end else begin
                    state_next = DATA_FETCH;
                end
            end

            OPERATION: begin
                state_next = DONE;
            end

            DONE: begin
                if (m_axis_tready) begin
                    state_next = IDLE;
                end else begin
                    state_next = DONE;
                end
            end

            default: begin
                state_next = IDLE;
            end
        endcase
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pixel_count <= 4'd0;
            m_axis_tvalid <= 1'b0;
            s_axis_tready <= 1'b1;
            m_axis_tdata <= 24'd0;
        end else begin
            case (state)
                IDLE: begin
                    pixel_count <= 4'd0;
                    m_axis_tvalid <= 1'b0;
                    s_axis_tready <= 1'b1;
                end

                DATA_FETCH: begin
                    if (s_axis_tvalid && s_axis_tready) begin
                        pixel_batch[pixel_count] <= s_axis_tdata;
                        pixel_count <= pixel_count + 1;
                        if (pixel_count == 4'd8) begin
                            s_axis_tready <= 1'b0;
                        end
                    end
                end

                OPERATION: begin
                    m_axis_tdata <= {result_r, result_g, result_b};
                    m_axis_tvalid <= 1'b1;
                end

                DONE: begin
                    if (m_axis_tready) begin
                        m_axis_tvalid <= 1'b0;
                        s_axis_tready <= 1'b1;
                    end
                end
            endcase
        end
    end

endmodule

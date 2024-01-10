module fir_filter #(
    parameter DATA_WIDTH = 16
) (
    input clk, 
    input reset, 
    input enable, 
    input wire signed [DATA_WIDTH-1:0] samples_in,
    input wire signed [(DATA_WIDTH*8)-1:0] fir_coeffs,
    output reg signed [(DATA_WIDTH*2)-1:0] filter_out
);

// Singed buffer registers
reg signed [DATA_WIDTH-1:0] buf0,
    buf1,
    buf2, 
    buf3, 
    buf4, 
    buf5, 
    buf6,
    buf7;

// Signed product registers
reg signed [(DATA_WIDTH*2)-1:0] product0,
    product1,
    product2, 
    product3, 
    product4, 
    product5, 
    product6,
    product7;

// Reset or shift buffers
always @(posedge clk) begin
    if (reset) begin 
        buf0 <= '0; 
        buf1 <= '0; 
        buf2 <= '0; 
        buf3 <= '0; 
        buf4 <= '0; 
        buf5 <= '0; 
        buf6 <= '0; 
        buf7 <= '0; 
    end else
        buf0 <= samples_in; 
        buf1 <= buf0;
        buf2 <= buf1;
        buf3 <= buf2;
        buf4 <= buf3;
        buf5 <= buf4;
        buf6 <= buf5;
        buf7 <= buf6;
end

// Pipeline Stage: multiply buffers x coefficients
always @(posedge clk) begin 
    if (enable) begin 
        product0 <= buf0 * $signed(fir_coeffs[0*DATA_WIDTH +:DATA_WIDTH]); 
        product1 <= buf1 * $signed(fir_coeffs[1*DATA_WIDTH +:DATA_WIDTH]); 
        product2 <= buf2 * $signed(fir_coeffs[2*DATA_WIDTH +:DATA_WIDTH]); 
        product3 <= buf3 * $signed(fir_coeffs[3*DATA_WIDTH +:DATA_WIDTH]); 
        product4 <= buf4 * $signed(fir_coeffs[4*DATA_WIDTH +:DATA_WIDTH]); 
        product5 <= buf5 * $signed(fir_coeffs[5*DATA_WIDTH +:DATA_WIDTH]); 
        product6 <= buf6 * $signed(fir_coeffs[6*DATA_WIDTH +:DATA_WIDTH]); 
        product7 <= buf7 * $signed(fir_coeffs[7*DATA_WIDTH +:DATA_WIDTH]);
    end
end

// Pipeline Stage: sum products of buffer x coefficient 
always @(posedge clk) begin 
    filter_out <=   product0 + 
                    product1 + 
                    product2 + 
                    product3 + 
                    product4 + 
                    product5 + 
                    product6 + 
                    product7;
end

endmodule
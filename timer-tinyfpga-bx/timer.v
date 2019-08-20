
module timer(
    input clk,
    input reset,
    output reg [31:0] data
);

    always @( posedge clk or negedge reset )
    begin

        if( ~reset )
            data <= 0;
        else
            data <= data + 1;
    end

endmodule



`define TRIGGER_COUNT 6

module top(
    input [`TRIGGER_COUNT-1:0] TRIGGERS,
    input RESET,
    input CLK,
    output LED,

    output DATA_READY,

    input DATA_CLK,
    output DATA_OUT,

    input HC_RXD,
    input HC_TXD,
    input HC_SET,
    output RESERVED,
);

    wire [31:0] timer_data;

    wire [`TRIGGER_COUNT-1:0] data_ready;
    wire [`TRIGGER_COUNT-1:0] enabled_triggers;
    wire [`TRIGGER_COUNT:0] shift;

    timer timer_0(
        .clk( CLK ),
        .reset( |(data_ready & enabled_triggers) ),
        .data( timer_data )
    );

    genvar i;
    generate
        for (i=0; i<`TRIGGER_COUNT; i=i+1) begin

            trigger_timer t(
                .clk( CLK ),
                .trigger( TRIGGERS[i] ),
                .reset( RESET ),
                .data( timer_data ),
                .data_ready( data_ready[i] ),
                .is_enabled( enabled_triggers[i] ),

                .data_clock( DATA_CLK ),
                .data_shiftin( shift[i+1] ),
                .data_shiftout( shift[i] )
            );
        end
    endgenerate

    assign shift[6] = 0;
    assign DATA_OUT = shift[0];
    assign DATA_READY = &data_ready;
    assign LED = ~|( data_ready & enabled_triggers );
    assign RESERVED = |(data_ready & enabled_triggers);


endmodule


module top(
    input [3:0] TRIGGERS,
    input RESET,
    input CLK,
    output LED,

    output DATA_READY,

    input DATA_CLK,
    output DATA_OUT
);

    wire [31:0] timer_data;

    timer timer_0(
        .clk( CLK ),
        .reset( |data_ready ),
        .data( timer_data )
    );

    wire [3:0] data_ready;

    wire t1_out;
    trigger_timer t1(
        .clk( CLK ),
        .trigger( TRIGGERS[0] ),
        .reset( RESET ),
        .data( timer_data ),
        .data_ready( data_ready[0] ),

        .data_clock( DATA_CLK ),
        .data_shiftin( 0 ),
        .data_shiftout( t1_out )
    );

    wire t2_out;
    trigger_timer t2(
        .clk( CLK ),
        .trigger( TRIGGERS[1] ),
        .reset( RESET ),
        .data( timer_data ),
        .data_ready( data_ready[1] ),

        .data_clock( DATA_CLK ),
        .data_shiftin( t1_out ),
        .data_shiftout( t2_out )
    );

    wire t3_out;
    trigger_timer t3(
        .clk( CLK ),
        .trigger( TRIGGERS[2] ),
        .reset( RESET ),
        .data( timer_data ),
        .data_ready( data_ready[2] ),

        .data_clock( DATA_CLK ),
        .data_shiftin( t2_out ),
        .data_shiftout( t3_out )
    );

    wire t4_out;
    trigger_timer t4(
        .clk( CLK ),
        .trigger( TRIGGERS[3] ),
        .reset( RESET ),
        .data( timer_data ),
        .data_ready( data_ready[3] ),

        .data_clock( DATA_CLK ),
        .data_shiftin( t3_out ),
        .data_shiftout( t4_out )
    );

    assign DATA_OUT = t4_out;
    assign DATA_READY = &data_ready;
    assign LED = data_ready[3];


endmodule

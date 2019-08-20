module output_register(
	input clk,
	
	input trigger,
	input reset,
	input [31:0] data,
	output reg [31:0] data_latched,
	output reg data_ready,
	
	input data_clock,
	input data_shiftin,
	output reg data_shiftout
);

	reg trigger_latched;
	reg data_clock_prev;
	
	reg data_clock_sync1, data_clock_sync2;
	
	always @( negedge clk or negedge reset )
	begin

		if( ~reset )
		begin
			data_clock_prev <= 0;
			data_ready <= 0;
			data_latched = 0;
			data_shiftout = 0;
			data_clock_sync1 <= 0;
			data_clock_sync2 <= 0;
		end
		else
		begin
		
			data_clock_sync1 <= data_clock;
			data_clock_sync2 <= data_clock_sync1;
		
			if( data_ready == 0 )
				data_latched = data;
				
			if( trigger )
				data_ready = 1;
			
			if( data_clock_sync2 == 1 && data_clock_prev == 0 )
			begin
				data_latched = { data_shiftin, data_latched[31:1] };
				data_clock_prev <= 1;
			end
				
			data_clock_prev <= data_clock_sync2;
			data_shiftout = data_latched[0];
		
		end
	end
					
endmodule

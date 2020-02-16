
module trigger_timer(
	input clk,
	
	input trigger,
	input reset,
	input [31:0] data,
	output reg data_ready,
	output reg is_enabled,
	
	input data_clock,
	input data_shiftin,
	output reg data_shiftout
);

	reg [32:0] data_latched;
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
			is_enabled <= 0;
		end
		else
		begin

			// This is enabled only if the trigger is ever zero.
			// Triggers that 
			if( ~trigger )
				is_enabled <= 1;
		
			data_clock_sync1 <= data_clock;
			data_clock_sync2 <= data_clock_sync1;
		
			if( data_ready == 0 )
				data_latched = { data, is_enabled };
				
			if( trigger )
				data_ready = 1;
			
			if( data_clock_sync2 == 1 && data_clock_prev == 0 )
			begin
				if( data_ready == 0 )
				begin
					data_ready = 1;
					data_latched = { -32'd2, is_enabled };
				end

				data_latched = { data_shiftin, data_latched[32:1] };
				data_clock_prev <= 1;
			end
				
			data_clock_prev <= data_clock_sync2;
			data_shiftout = data_latched[0];
		end
	end
					
endmodule

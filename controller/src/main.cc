
#include <Arduino.h>

#define DATA_READY D2
#define DATA_CLOCK D3
#define DATA_INPUT D1
#define DATA_ANY D0
#define RESET D4

#define TRIGGER_COUNT 6

void setup()
{
	Serial.begin( 9600 );
	pinMode( DATA_CLOCK, OUTPUT );
	pinMode( DATA_INPUT, INPUT );
	pinMode( DATA_READY, INPUT );
	pinMode( DATA_ANY, INPUT );
	pinMode( RESET, OUTPUT );

	digitalWrite( RESET, 1 );
}

uint32_t readTime()
{
	bool enabled = digitalRead( DATA_INPUT );
	digitalWrite( DATA_CLOCK, 1 );
	digitalWrite( DATA_CLOCK, 0 );

	uint32_t result = 0;
	for( int b = 0; b < 32; b++ )
	{
		result += digitalRead( DATA_INPUT ) << b;

		digitalWrite( DATA_CLOCK, 1 );
		digitalWrite( DATA_CLOCK, 0 );
	}

	return enabled ? result : -1;
}

void loop()
{
	int s = Serial.read();
	if( s == 'r' )
	{
		digitalWrite( RESET, 0 );
		delay(100);
		digitalWrite( RESET, 1 );
	}

	if( digitalRead( DATA_READY ) )
	{
		for( int i = 0; i < TRIGGER_COUNT; i++ )
		{
			Serial.print( (int32_t) readTime() );
			Serial.print( ";" );
		}
		Serial.println();

		delay( 1000 );

		digitalWrite( RESET, 0 );
		digitalWrite( RESET, 1 );
	}

	if( digitalRead( DATA_ANY ) )
	{
		delay( 100 );
		if( ! digitalRead( DATA_READY ) )
		{
			for( int i = 0; i < TRIGGER_COUNT; i++ )
			{
				Serial.print( (int32_t) readTime() );
				Serial.print( ";" );
			}
			Serial.println( "  SPURIOUS" );

			delay( 500 );

			digitalWrite( RESET, 0 );
			digitalWrite( RESET, 1 );
		}
	}
}

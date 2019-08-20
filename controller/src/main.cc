
#include <Arduino.h>

#define DATA_READY D0
#define DATA_CLOCK D1
#define DATA_INPUT D2
#define RESET D3
#define TRIGGER1 D5
#define TRIGGER2 D6
#define TRIGGER3 D7
#define TRIGGER4 D8

void setup()
{
	Serial.begin( 9600 );
	pinMode( DATA_CLOCK, OUTPUT );
	pinMode( DATA_INPUT, INPUT );
	pinMode( DATA_READY, INPUT );
	pinMode( RESET, OUTPUT );
	pinMode( TRIGGER1, OUTPUT );
	pinMode( TRIGGER2, OUTPUT );
	pinMode( TRIGGER3, OUTPUT );
	pinMode( TRIGGER4, OUTPUT );

	digitalWrite( RESET, 1 );
}

uint32_t readTime()
{
	uint32_t result = 0;
	for( int b = 0; b < 32; b++ )
	{
		result += digitalRead( DATA_INPUT ) << b;

		digitalWrite( DATA_CLOCK, 1 );
		digitalWrite( DATA_CLOCK, 0 );
	}

	return result;
}

void loop()
{
	int b = Serial.read();
	if( b == 'b' )
	{
		digitalWrite( TRIGGER1, 1 );
		delay(1000);
		digitalWrite( TRIGGER2, 1 );
		delay(1000);
		digitalWrite( TRIGGER3, 1 );
		delay(1000);
		digitalWrite( TRIGGER4, 1 );
		digitalWrite( TRIGGER1, 0 );
		digitalWrite( TRIGGER2, 0 );
		digitalWrite( TRIGGER3, 0 );
		digitalWrite( TRIGGER4, 0 );
	}

	if( digitalRead( DATA_READY ) )
	{
		int32_t t1 = (int32_t) readTime();
		int32_t t2 = (int32_t) readTime();
		int32_t t3 = (int32_t) readTime();
		int32_t t4 = (int32_t) readTime();

		Serial.print( t1 );
		Serial.print( ";" );
		Serial.print( t2 );
		Serial.print( ";" );
		Serial.print( t3 );
		Serial.print( ";" );
		Serial.println( t4 );

		delay( 1000 );

		digitalWrite( RESET, 0 );
		digitalWrite( RESET, 1 );
	}

	/*
	if( digitalRead( ANY_READY ) )
	{
		delay( 100 );
		if( ! digitalRead( DATA_READY ) )
		{
			Serial.println( "SPURIOUS" );

			delay( 500 );

			digitalWrite( RESET, 0 );
			digitalWrite( RESET, 1 );
		}
	}
	*/
}

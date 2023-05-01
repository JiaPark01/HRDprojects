#ifndef MY_ARDUINO_LIB_H
#define MY_ARDUINO_LIB_H

#define LED1 0
#define LED2 1
#define LED3 2
#define LED4 3
#define LED5 4
#define LED6 5
#define LED7 6
#define LED8 7

#define ON    1
#define OFF   0
#define _ON   0
#define _OFF  1

#define bit_set(ADDRESS, BIT) (ADDRESS |= (1<<BIT)) // bit high
#define bit_clr(ADDRESS, BIT) (ADDRESS &= ~(1<<BIT))  // bit low
#define bit_chk(ADDRESS, BIT) (ADDRESS & (1<<BIT))    // bit check
#define bit_tg(PORT, BIT) (PORT ^= (1<<BIT))    //bit toggle

#define d_out(pin, value) digitalWrite(pin, value)

void byte_out(unsigned char data)
{
  d_out(LED1, data % 2);        // bit 0 = lsb
  d_out(LED2, data / 2 % 2);    // bit 1
  d_out(LED3, data / 4 % 2);    // bit 2
  d_out(LED4, data / 8 % 2);    // bit 3
  d_out(LED5, data / 16 % 2);   // bit 4
  d_out(LED6, data / 32 % 2);   // bit 5
  d_out(LED7, data / 64 % 2);   // bit 6
  d_out(LED8, data / 128 % 2);  // bit 7 = msb

}

#endif

//사용법
// d_out(LED1, ON);
// bit_set(PORTD, 5);
// bit_clr(PORTD, 3);
// if(bit_chk(PIND, 3)) {}
// bit_tg(PORTD, 0);
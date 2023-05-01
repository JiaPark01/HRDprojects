#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <LiquidCrystal.h>




// setup ultrasonic
#define trig A0
#define echo A1


// setup lcd
const int rs = 8, en = 9, d4 = 4, d5 = 5, d6 = 6, d7 = 7;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

#define LCD_IF_8_Bit  1
#define LCD_PD        1

#include "my_arduino_lib.h"
#include "my_lcd_Arduino_lib_v2_3.h"

char d_buf[20]; 


// setup led
#define LED 3

// setup buzzer
#define BUZZER 10
#define ring() tone(BUZZER, 800)

void setup() {
  // ultrasonic
  pinMode(trig, OUTPUT);
  pinMode(echo, INPUT);

  // lcd
  DDRD = 0xff;  // use as output
  DDRB = 0xff;
  PORTD = 0x00;
  PORTB = 0x00;
  lcd_init();

  lcd.begin(16, 2);

  Serial.begin(9600);
  Serial.println("dd");
}

void loop() {
  // ultrasonic
  digitalWrite(trig, HIGH);
  delay(10);
  digitalWrite(trig, LOW);

  long distance = pulseIn(echo, HIGH) / 58;

  Serial.println(distance, DEC);
  
  // lcd
  lcd.setCursor(0, 0);
  sprintf(d_buf, "Distance: %3ldcm", distance);
  lcd.print(d_buf);


  // led & buzzer
  if (distance < 5) {
    digitalWrite(LED, ON);
    ring();
    delay(50);
    digitalWrite(LED, OFF);
    noTone(BUZZER);
    delay(50);
  }
  else if (distance < 10) {
    digitalWrite(LED, ON);
    ring();
    delay(100);
    digitalWrite(LED, OFF);
    noTone(BUZZER);
    delay(100);
  } else if (distance < 30) {
    digitalWrite(LED, ON);
    ring();
    delay(500);
    digitalWrite(LED, OFF);
    noTone(BUZZER);
    delay(500);
  } else delay (500);
  
  
}

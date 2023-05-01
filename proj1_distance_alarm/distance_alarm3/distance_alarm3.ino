#include <MsTimer2.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <LiquidCrystal.h>


// setup ultrasonic
#define trigPin A0
#define echoPin A1

unsigned long distance, prevTime = millis(), mPrevTime = millis(), now = millis();
unsigned int cnt; 
int ledFlag = 0;
bool timeFlag = 0;

long time1;
  long time2;
// setup lcd
const int rs = 8, en = 9, d4 = 10, d5 = 11, d6 = 12, d7 = 13;  
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

#define LCD_PD        1

#include "my_arduino_lib.h"
#include "my_lcd_Arduino_lib_v2_3.h"
#include "rc_motor.h"  // RC 카의 모터 조종 관련 함수들이 포함된 헤더파일. 전진, 후진, 좌회전, 우회전, 정지 코드들이 있음

char dist_buf[20];


// setup led
#define LED 2

// setup buzzer
#define BUZZER 3

void ring(unsigned int state)  // 부저를 이용한 특정 주파수의 경고음 활성화 코드를 간단하게 사용하기 위해 함수 구현
{
  if(state == 1) tone(BUZZER, 800, 100);
  else noTone(BUZZER);
}

void ledBuz()
{
  if (ledFlag == 0) {
    digitalWrite(LED, 1);
    ring(1);
    ledFlag = 1;
     Serial.println('k');
  } else if (ledFlag == 1) {
    digitalWrite(LED, 0);
    ring(0);
    ledFlag = 0;
     Serial.println("y");
  }
  Serial.println(ledFlag);
}



void setup() {
  // rc car - 각 모터마다 전진/후진 핀이 사용됨. 먼저 한쪽 방향을 LOW로 멈춘 뒤 HIGH로 변경해야 함. 예를 들어 전진을 하려면 양측 후진 모터를 LOW (OFF)로 설정한 뒤 전진 모터를 HIGH (ON)로 설정해야함
  pinMode(rMfwd, OUTPUT);           // 오른쪽 모터 전진
  pinMode(rMback, OUTPUT);          // 오른쪽 모터 후진
  pinMode(lMback, OUTPUT);          // 왼쪽 모터 후진
  pinMode(lMfwd, OUTPUT);           // 왼쪽 모터 전진

  // ultrasonic
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // lcd & led
  DDRD = 0xff;  // use as output
  DDRB = 0xff;
  PORTD = 0x00;
  PORTB = 0x00;
  lcd_init();

  lcd.begin(16, 2);

  Serial.begin(9600);
  MsTimer2::set(100, ledBuz);
  MsTimer2::start();
}

void loop() {

  // ultrasonic
  digitalWrite(trigPin, ON);              // 음파 방출 핀을 HIGH로 설정
  delay(10);
  digitalWrite(trigPin, OFF);             // 0.01초 후 음파 방출을 멈춤

 // long distTime = pulseIn(echoPin, ON);
 // long distance = distTime / 58;  // 돌아오는 음파를 감지하여 방출 이후부터 돌아오기까지 걸린 시간을 계산하여 거리를 구함
  // Serial.print("disttime: ");
  // Serial.println(distTime);

  // Serial.print("dist: ");
  // Serial.println(distance, DEC);              // 거리를 시리얼 모니터로 확인하기 위한 코드. RC카와 연결된 LCD가 잘 작동하지 않을 수 있어 소프트웨어 문제인지 하드웨어 문제인지 버그 색출용으로 사용


  // lcd
  lcd.setCursor(0, 0);
  sprintf(dist_buf, "Distance: %4ldcm", distance);
  lcd.print(dist_buf);
  
  // rc car
  if (distance < 20) {                       // 장애물과 거리가 20cm로 매우 가까워지면 0.5초간 후진 후 0.3초 동안 우회전을 함. 장애물이 사라질 때까지 반복하며
    back();
    delay(500);
    right();
    delay(300);
  } else {                                    // 장애물이 없을 경우 전진함
    forward();
    delay(500);
  }

  // time1 = millis();
  // long lenMotor = time2 - time1;
  // if (distance < 20) {
  //   now = millis();
  //   // if (now - mPrevTime > 1000 && now - mPrevTime < 1799) mPrevTime += 1000;
  //   // Serial.println(millis());
  //   // Serial.println(mPrevTime);
  //   // Serial.println(millis() - mPrevTime);
  //   // Serial.println();

  //   if(now - mPrevTime < 1000 + lenMotor) {
  //     back();
  //     Serial.print("diff: ");
  //     Serial.println(now - mPrevTime);
  //      Serial.print("mPrev: ");
  //     Serial.println(mPrevTime);
  //      Serial.print("now: ");
  //      Serial.println(millis());
  //      Serial.println();
  //   } else if(now - mPrevTime < 3000 + lenMotor) {
  //     Serial.print("diff: ");
  //     Serial.println(now - mPrevTime);
  //     right();
  //   } else mPrevTime = millis();
    
  // } else {
  //   mPrevTime = millis();
  //   // Serial.print("resetted: ");
  //   // Serial.print("diff: ");
  //   //   Serial.println(millis() - mPrevTime);
  //   //    Serial.print("mPrev: ");
  //   //   Serial.println(mPrevTime);
  //   //    Serial.print("now: ");
  //   // Serial.print("now2: ");
  //   // Serial.println(millis());
  //   // Serial.println();
  //   forward();
  // } 
  // long time2 = millis();

// if (ledFlag == 0) {
//   MsTimer2::set(50, ledBuzOn);
//   MsTimer2::start();
//   ledFlag = 1;
// } else {
//   MsTimer2::set(50, ledBuzOff);

//   MsTimer2::start();
//   ledFlag = 0;
// }

//Serial.println(ledFlag);

// if(distance < 50)
//   {
//     if (timeFlag == 0) {
//       MsTimer2::set(50, ledBuz);
//       MsTimer2::start();
//       timeFlag = 1;
//     }
//   } //else MsTimer2::stop();

// if(distance < 50)
//   {
//     MsTimer2::stop();
//     MsTimer2::set(50, ledBuz);
//     MsTimer2::start();
//   } else if(distance < 70) {
//     MsTimer2::stop();
//     MsTimer2::set(70, ledBuz);
//     MsTimer2::start();
//   } else if(distance < 100) {
//     MsTimer2::stop();
//     MsTimer2::set(100, ledBuz);
//     MsTimer2::start();
//   } else
//   {
//     MsTimer2::stop();
//     digitalWrite(LED, OFF);
//     ring(0);
//   }
  
  // // led & buzzer
  // if (distance < 50) {
  //   digitalWrite(LED, ON);
  //   ring();
  //   delay(50);
  //   digitalWrite(LED, OFF);
  //   noTone(BUZZER);
  //   delay(50);
  // }
  // else if (distance < 70) {
  //   digitalWrite(LED, ON);
  //   ring();
  //   delay(100);
  //   digitalWrite(LED, OFF);
  //   noTone(BUZZER);
  //   delay(100);
  // } else if (distance < 100) {
  //   digitalWrite(LED, ON);
  //   ring();
  //   delay(500);
  //   digitalWrite(LED, OFF);
  //   noTone(BUZZER);
  //   delay(500);
  // } else delay (500);
  
}

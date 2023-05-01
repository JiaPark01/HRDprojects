#include <MsTimer2.h>
#include <LiquidCrystal.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>


#define trigPin  A0
#define echoPin  A1
#define BUZZER   9
#define LED      10

#define ring() tone(BUZZER, 800)

const int rs = 3, en = 4, d4 = 5, d5 = 6, d6 = 7, d7 = 8;



LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

int ad_buf1, ad_buf2; 
char d_buf[20]; // 거리1
char d_buf2[20]; // 거리2
char d_buf3[20];
long dist1, dist2, distance;
long spd; // 속력
long time, t;


void time2_irq()
{

  // 거리2 측정
  digitalWrite(trigPin,HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin,LOW);
  
  time = pulseIn(echoPin,HIGH);
  distance = time / 58;
  time += time;  
}



void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  
  DDRD = 0xff;
  DDRB = 0xff;
  PORTD = 0x00;
  PORTB = 0x00;

  Serial.begin(9600);
  //pinMode(BUZZER,OUTPUT);
  lcd.begin(16,2);

  do
  {
    // 거리2 측정
    digitalWrite(trigPin,HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin,LOW);
    
    dist1 = pulseIn(echoPin,HIGH) / 58;
  }while(dist1 > 1000);

  MsTimer2::set(1, time2_irq);
  MsTimer2::start();


}

void loop() {

  // do 
  // {
  //   // 거리 1 측정
  //   digitalWrite(trigPin,HIGH);
  //   delayMicroseconds(10);
  //   digitalWrite(trigPin,LOW);
    
  //   dist1 = pulseIn(echoPin,HIGH) / 58;
  // }
  // while(dist1 > 1000);
  
  // do
  // {
  //   // 거리2 측정
  //   digitalWrite(trigPin,HIGH);
  //   delayMicroseconds(10);
  //   digitalWrite(trigPin,LOW);
    
  //   dist2 = pulseIn(echoPin,HIGH) / 58;
  // }while(dist2 > 1000);
  
  do
  {
    dist2 = distance;
    t = time;
  } while(dist2 > 1000);

  // 거리출력
  Serial.print(dist2,DEC); //DEC == 10진수
  Serial.println("CM");
  lcd.setCursor(0, 0);
  sprintf(d_buf,"DIST :%4d  CM",dist1);
  lcd.print(d_buf);

  // 속력출력 -- 추후 시간 조정 필요
  
  // 속력 계산
  if(dist1>dist2) spd = ((dist1-dist2)*3600000/time);
  else spd = ((dist2-dist1)*3600000/time);
  // time = 0;
  // 출력
  lcd.setCursor(0, 1);
  sprintf(d_buf2,"Spd  :%5d",spd);
  lcd.print(d_buf2);
  lcd.setCursor(13,1);
  sprintf(d_buf3,"m/h");
  lcd.write(d_buf3);
  
  // led & buzze
  if (dist2 < 5) {
    digitalWrite(LED, 1);
    ring();
    delay(50);
    digitalWrite(LED, 0);
    noTone(BUZZER);
    delay(50);
  }
  else if (dist2 < 10) {
    digitalWrite(LED, 1);
    ring();
    delay(100);
    digitalWrite(LED, 0);
    noTone(BUZZER);
    delay(100);
  } else if (dist2 < 30) {
    digitalWrite(LED, 1);
    ring();
    delay(500);
    digitalWrite(LED, 0);
    noTone(BUZZER);
    delay(500);
  } else delay (500);

  dist1 = dist2;
}

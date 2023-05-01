#include "Arduino.h"
#ifndef RC_MOTOR_H
#define RC_MOTOR_H

// setup rc car
#define lMfwd   4     // left motor forward
#define lMback  5
#define rMfwd   6     // right motor fwd
#define rMback  7

// rc car func

void forward()
{
  digitalWrite(rMback, OFF);
  digitalWrite(lMback, OFF);
  delay(1000);

  digitalWrite(rMfwd, ON);
  digitalWrite(lMfwd, ON);
}

void back()
{
  digitalWrite(rMfwd, OFF);
  digitalWrite(lMfwd, OFF);

  delay(1000);
  digitalWrite(rMback, ON);
  digitalWrite(lMback, ON);
}

void left()
{
  digitalWrite(rMback, OFF);
  digitalWrite(lMfwd, OFF);

  delay(1000);
  digitalWrite(rMfwd, ON);
  digitalWrite(lMback, ON);

}

void right()
{
  digitalWrite(rMfwd, OFF);
  digitalWrite(lMback, OFF);
  delay(1000);
  digitalWrite(rMback, ON);
  digitalWrite(lMfwd, ON);
}

void stop()
{
  analogWrite(rMfwd, OFF);
  analogWrite(lMback, OFF);
  digitalWrite(rMback, OFF);
  digitalWrite(lMfwd, OFF);
}

#endif
import socket
import threading
import smbus
from time import sleep
import RPi.GPIO as GPIO

MODE1 = 0x00
PRE_SCALE = 0xFE
LED0_OFF_L = 0x06
LED0_OFF_H = 0x07
LED0_OFF_L = 0x08
LED0_OFF_H = 0x09

REG_ALL_ON_L = 0xFA
REG_ALL_ON_H = 0xFB
REG_ALL_OFF_L = 0xFC
REG_ALL_OFF_H = 0xFD

SLEEP = 0x10
RESTART = 0x80

class PWM:
    def __init__(self, bus, address=0x5E): #chip address 0x5e
        self.bus = bus
        self.address = address
        self.writeByte(MODE1, 0x00)

    def set_frequency(self, frequency):
        #print(f"frequency : {frequency}")
        base_mode = self.readByte(MODE1) & 0xFF
        self.writeByte(MODE1, base_mode | SLEEP)

        prescale = (25000000.0 / (4096 * frequency) + 0.5) - 1

        self.writeByte(PRE_SCALE, int(prescale))
        self.writeByte(MODE1, base_mode)

        sleep(0.001)

        self.writeByte(MODE1, base_mode | RESTART)

    def set_duty(self, pin, duty_cycle):
        channel = pin * 4
        duty_off = int(duty_cycle) & 0xFFFF
        self.writeByte(LED0_OFF_L + channel, duty_off & 0xFF)
        self.writeByte(LED0_OFF_H + channel, duty_off >> 8)

    def writeByte(self, register, value):
        try:
            #print(f'vlaue : {value} , type : {type(value)}')
            self.bus.write_byte_data(self.address, register, value)
        except:
            print("Error writing to I2C by writeByte")
            pass

    def readByte(self, register):
        try:
            value = self.bus.read_byte_data(self.address, register)
            #print(f"value : {value} , type : {type(value)}")
            return value
        except:
            print("Error writing to I2C by readByte")
            return None

SERVO = 3
GPIO.setmode(GPIO.BCM)
leds = [23, 24, 25, 1]                                  # leds 1, 2, 3, 4
for i in leds:                                          # for all leds, set them as output
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.LOW)

HOST = 'localhost'
PORT = 9999

i2c_bus = smbus.SMBus(1)
pwm = PWM(i2c_bus)
pwm.set_frequency(60)
pwm.set_duty(SERVO, 540)

def flash(led):                                         # a simple flashing twice in a row, the led depends on whether its locking or unlocking
    for i in range(2):                                  # repeat twice
        GPIO.output(leds[led], GPIO.HIGH)               # turn the led on. if led == 0, LED1, if led == 3, LED4
        sleep(0.1)
        GPIO.output(leds[led], GPIO.LOW)                # turn off the led after 0.1 seconds
        sleep(0.1)

def receive_message(clnt):                             # when receive a message from doorlock_client.cpp
    while True:                                         # loop it until esc is pressed
        data = clnt.recv(1024).decode(encoding='utf-8') # read message from the server

        if data == "open":                              # if the message received is "open"
            flash(3)                                    # flash LED4 twice
            cnt = 0
            for i in range(540, 0, -100):               # to blink led and run servo motor. from 540 degrees, decrease by 100
                if i % 100 == 40 and i // 100 % 2 == 1: # at i == 540, 340, 140
                    GPIO.output(leds[cnt], GPIO.HIGH)   # turn on the led, in order of 1 2 3 at each loop
                if i % 100 == 40 and i // 100 % 2 == 0: # at i == 440, 240, 40
                    GPIO.output(leds[cnt], GPIO.LOW)    # turn off the led
                    cnt += 1                            # increase cnt to change which LED to blink next
                pwm.set_duty(SERVO, i)                  # spin servo motor at each blink
                sleep(0.105)                            # pause between blinks
            sleep(5)                                    # give 5 seconds before locking again
            
            flash(0)                                    # flash LED1 twice
            for i in range(540, 0, -100):               # to blink led and run servo motor. from 540 degrees, decrease by 100
                if i % 100 == 40 and i // 100 % 2 == 1: # at i == 540, 340, 140
                    GPIO.output(leds[cnt], GPIO.HIGH)   # turn on the led, in order of 1 2 3 at each loop
                if i % 100 == 40 and i // 100 % 2 == 0: # at i == 440, 240, 40
                    GPIO.output(leds[cnt], GPIO.LOW)    # turn off the led
                    cnt -= 1                            # decrease cnt to change which LED to blink next (opposite direction to unlock)
                pwm.set_duty(SERVO, 540 - i)            # spin servo motor at each blink (opposite direction to unlock)
                sleep(0.105)                            # pause between blinks
            sleep(5)                                    # give 5 seconds before the door can be unlocked again
            

with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0) as clnt:
    try:
        clnt.connect((HOST, PORT))
        
        stop = threading.Event()                        # used to keep the leds on or off for certain amount of time

        t = threading.Thread(target=receive_message, args=(clnt,))
        t.start()
        t.join()

    except KeyboardInterrupt:
        print("Bye")
        GPIO.cleanup()                                  # turn off everything before closing the prg
        i2c_bus.close()                                 # shut down servo motor
    
    finally:
        GPIO.cleanup()                                  # turn off everything before closing the prg
        i2c_bus.close()    
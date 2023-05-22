# v1    : basic test for creating py file

import cv2
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
LED = 1
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)

i2c_bus = smbus.SMBus(1)
pwm = PWM(i2c_bus)
pwm.set_frequency(60)

def flash():
    for i in range(2):
        GPIO.output(LED, GPIO.HIGH)
        sleep(0.1)
        GPIO.output(LED, GPIO.LOW)
        sleep(0.1)

model = "res10_300x300_ssd_iter_140000_fp16.caffemodel"
config = "deploy.prototxt"

try:
    pass
        
except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()   
    i2c_bus.close()

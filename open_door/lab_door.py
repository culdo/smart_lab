#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

servoPIN = 12
vccPIN = 8
GPIO.setmode(GPIO.BOARD)
GPIO.setup(servoPIN, GPIO.OUT)
GPIO.setup(vccPIN, GPIO.OUT)
p = GPIO.PWM(servoPIN, 50)  # GPIO 17 for PWM with 50Hz
p.start(12.5)  # Initialization with %2.5

def open_door(open_angle=5.0, interval=1.0):
  GPIO.output(vccPIN, GPIO.HIGH)
  p.ChangeDutyCycle(5.0)
  time.sleep(interval)
  p.ChangeDutyCycle(12.5)
  time.sleep(interval)
  GPIO.output(vccPIN, GPIO.LOW)

if __name__ == "__main__":
    open_door()

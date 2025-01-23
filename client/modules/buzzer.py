from config import *
import RPi.GPIO as GPIO
import time

def buzz_once(delta=.5):
    GPIO.output(buzzerPin, False)
    time.sleep(delta)
    GPIO.output(buzzerPin, True)
    time.sleep(delta)

#!/usr/bin/env python3
import RPi.GPIO as GPIO
from config import *

_left_callback = None
_right_callback = None

last_state = (0, 0)

def setup_encoder():
    global last_state
    last_state = (GPIO.input(encoderLeft), GPIO.input(encoderRight))
    GPIO.add_event_detect(encoderLeft, GPIO.BOTH, callback=encoder_event, bouncetime=1)
    GPIO.add_event_detect(encoderRight, GPIO.BOTH, callback=encoder_event, bouncetime=1)

def encoder_event(channel):
    global last_state, _left_callback, _right_callback

    current_state = (GPIO.input(encoderLeft), GPIO.input(encoderRight))

    if last_state == (0, 1) and current_state == (1, 1):
        if _right_callback:
            _right_callback()
    elif last_state == (1, 0) and current_state == (1, 1):
        if _left_callback:
            _left_callback()

    last_state = current_state

def assign_encoder_left_callback(callback):
    global _left_callback
    _left_callback = callback

def assign_encoder_right_callback(callback):
    global _right_callback
    _right_callback = callback

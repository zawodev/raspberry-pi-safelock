import time
import config
import RPi.GPIO as GPIO

def default_callback():
    pass

red_button_callback = default_callback
green_button_callback = default_callback

def debounce(channel):
    time.sleep(0.05)  # opóźnienie 50 ms (debounce)
    if GPIO.input(channel) == GPIO.LOW:
        if channel == config.buttonRed and red_button_callback:
            red_button_callback()
        elif channel == config.buttonGreen and green_button_callback:
            green_button_callback()

def assign_red_button_callback(callback):
    """przypisuje funkcję do czerwonego przycisku"""
    global red_button_callback
    red_button_callback = callback

def assign_green_button_callback(callback):
    """przypisuje funkcję do zielonego przycisku"""
    global green_button_callback
    green_button_callback = callback

# konfiguracja przycisków z obsługą zdarzeń
GPIO.add_event_detect(config.buttonRed, GPIO.FALLING, callback=debounce, bouncetime=200)
GPIO.add_event_detect(config.buttonGreen, GPIO.FALLING, callback=debounce, bouncetime=200)

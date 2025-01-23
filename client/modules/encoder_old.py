from config import *
import RPi.GPIO as GPIO

def default_callback():
    pass

left_callback = default_callback
right_callback = default_callback

# Śledzenie poprzednich stanów
last_state_a = GPIO.input(encoderLeft)
last_state_b = GPIO.input(encoderRight)

def encoder_callback(channel):
    global last_state_a, last_state_b

    # Aktualne stany kanałów
    state_a = GPIO.input(encoderLeft)
    state_b = GPIO.input(encoderRight)

    # Logika określająca kierunek
    if last_state_a == GPIO.LOW and state_a == GPIO.HIGH:  # Wzrost na A
        if state_b == GPIO.LOW:
            #print("left")
            left_callback()
        else:
            #print("right")
            right_callback()
    elif last_state_a == GPIO.HIGH and state_a == GPIO.LOW:  # Opadanie na A
        if state_b == GPIO.HIGH:
            #print("left")
            left_callback()
        else:
            #print("right")
            right_callback()

    # Aktualizacja stanów
    last_state_a = state_a
    last_state_b = state_b
    #print("callback")  # Potwierdzenie wywołania

# Funkcje przypisania callbacków
def assign_encoder_left_callback(callback):
    global left_callback
    left_callback = callback

def assign_encoder_right_callback(callback):
    global right_callback
    right_callback = callback

# Dodaj detekcję zdarzeń na obu kanałach
GPIO.add_event_detect(encoderLeft, GPIO.BOTH, callback=encoder_callback)
GPIO.add_event_detect(encoderRight, GPIO.BOTH, callback=encoder_callback)

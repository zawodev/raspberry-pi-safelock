import time
import neopixel
import board

from default_callback import default_callback
from modules.buzzer import buzz_once
from modules.buttons import assign_red_button_callback, assign_green_button_callback
from modules.encoder import assign_encoder_left_callback, assign_encoder_right_callback, setup_encoder
from modules.diodes import display_progress
from modules.oled_display import display_image_from_path

from modules.rfid_reader import RfidReader
from mqtt_client import MqttClient

from captcha import Captcha
from encoder_lock import EncoderLock
from green_button_test import GreenButtonTest

class Safe:
    def __init__(self):
        self.mqtt_client = MqttClient()
        self.pixels = neopixel.NeoPixel(board.D18, 8, brightness=1.0/32, auto_write=False)
        self.pixels.fill((0, 0, 0))
        self.pixels.show()
        self.rfid = RfidReader()
        setup_encoder()
        
        self.captcha = Captcha(self.create_path("catpcha.png"))
        self.encoder_lock = EncoderLock(self.pixels)
        self.green_button_test = GreenButtonTest()
        
        self.current_test = 0
        self.current_rfid = ""
        self.last_activity_time = time.time()
        self.timeout_seconds = 60

        self.running = True
           
# =========================================================================
# ------------------------------    MAIN    -------------------------------
# =========================================================================
    
    def create_path(self, file_name):
        return f"/home/pi/tests/mini-project/client/modules/lib/oled/{file_name}"

    def reset_to_start(self):
        self.current_rfid = ""
        self.set_progress(0)
        
        assign_encoder_left_callback(default_callback)
        assign_encoder_right_callback(default_callback)
        assign_red_button_callback(default_callback)
        assign_green_button_callback(default_callback)
        
        display_image_from_path(self.create_path("0locked.png"))
        time.sleep(1)
        self.setup_rfid_test()
        
    def set_progress(self, progress):
        self.current_test = progress
        display_progress(progress)

# =========================================================================
# ------------------------------    TESTS    ------------------------------
# =========================================================================

    def setup_rfid_test(self): #test 1 - RFID
        def handle_server_response(response):
            if response == "VALID":
                buzz_once()
                self.rfid.running = False
            elif response == "INVALID":
                buzz_once()
                buzz_once()
                self.rfid.running = True
            else:
                buzz_once()
                buzz_once()
                buzz_once()
                print("unknown response from server: ", response)
                
        def on_card_scanned(uid_num, uid_list, now_str):
            self.mqtt_client.set_callback("RFID", handle_server_response)
            msg_str = f"{uid_num},{now_str}"
            self.current_rfid = uid_num
            self.mqtt_client.publish("RFID", msg_str)
        
        display_image_from_path(self.create_path("1rfid.png"))
        self.rfid.set_callback(on_card_scanned)
        self.rfid.detect_card_once()
        self.set_progress(1)
        self.setup_captcha_test()
        
    def setup_captcha_test(self): #test 2 - CAPTCHA
        assign_encoder_left_callback(lambda: self.captcha.translate_piece(-1))
        assign_encoder_right_callback(lambda: self.captcha.translate_piece(1))

        def on_confirm():
            if self.captcha.confirm_position():
                buzz_once()
                self.captcha.running = False
            else:
                buzz_once()
                buzz_once()

        assign_red_button_callback(lambda: self.captcha.switch_axis())
        assign_green_button_callback(on_confirm)
        self.captcha.run()
        self.set_progress(2)
        self.setup_encoder_lock_test()
        
    def setup_encoder_lock_test(self): #test 3 - ENCODER LOCK
        assign_encoder_left_callback(lambda: self.encoder_lock.encoder_left_callback())
        assign_encoder_right_callback(lambda: self.encoder_lock.encoder_right_callback())
        assign_red_button_callback(lambda: self.encoder_lock.red_button_callback())
        assign_green_button_callback(lambda: self.encoder_lock.green_button_callback())

        def handle_server_response(response):
            if response == "VALID":
                self.encoder_lock.running = False
                buzz_once()
            elif response == "INVALID":
                buzz_once()
                buzz_once()
            else:
                buzz_once()
                buzz_once()
                buzz_once()
                print("unknown response from server: ", response)

        def on_confirm(hue_values):
            self.mqtt_client.set_callback("ENCODER_LOCK", handle_server_response)
            msg_str = f"{self.current_rfid}:{','.join(map(str, hue_values))}"
            self.mqtt_client.publish("ENCODER_LOCK", msg_str)

        display_image_from_path(self.create_path("3encoder.jpg"))
        self.encoder_lock.assign_confirm_callback(lambda: on_confirm(self.encoder_lock.hue_values))
        self.encoder_lock.run()
        self.pixels.fill((0, 0, 0))
        self.pixels.show()
        self.set_progress(3)
        self.setup_button_test()

    def setup_button_test(self): #test 4 - BUTTONS
        assign_green_button_callback(self.green_button_test.press_button)
        assign_red_button_callback(default_callback)
        assign_encoder_right_callback(default_callback)
        assign_encoder_left_callback(default_callback)
        def on_green_pressed():
            buzz_once()
            self.green_button_test.running = False
            time.sleep(1)
            
        display_image_from_path(self.create_path("4button.jpg"))
        self.green_button_test.set_callback(on_green_pressed)
        self.green_button_test.run()
        self.set_progress(4)
        self.on_success()

    def on_success(self):
        print("Access granted!")
        assign_green_button_callback(default_callback)
        display_image_from_path(self.create_path("0unlocked.png"))
        time.sleep(1)
        self.reset_to_start()
        

if __name__ == "__main__":
    safe = Safe()
    safe.reset_to_start()

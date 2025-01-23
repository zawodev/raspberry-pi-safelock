import time
from default_callback import default_callback

class GreenButtonTest:
    def __init__(self):
        self.running = False
        self.confirm_callback = default_callback
    
    def set_callback(self, callback):
        self.confirm_callback = callback
        
    def press_button(self):
        self.confirm_callback()

    def run(self):
        self.running = True
        while self.running:
            time.sleep(0.1)

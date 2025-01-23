import time
from default_callback import default_callback

class EncoderLock:
    def __init__(self, pixels):
        self.pixels = pixels
        self.current_index = 0  # index aktualnie edytowanej diody
        self.hue_values = [0] * 8  # obecne wartości HUE dla każdej diody
        self.running = False
        self.confirm_callback = default_callback

    def hue_to_rgb(self, hue, saturation=1.0, brightness=1.0):
        h = hue # 0-360
        s = saturation
        v = brightness

        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c

        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)

    def update_leds(self):
        for i in range(len(self.hue_values)):
            if i < self.current_index:
                r, g, b = self.hue_to_rgb(self.hue_values[i], brightness=.25)
            elif i == self.current_index:
                r, g, b = self.hue_to_rgb(self.hue_values[i], brightness=1.0)
            else:
                r, g, b = self.hue_to_rgb(self.hue_values[i], brightness=.25)
            self.pixels[i] = (r, g, b)
        self.pixels.show()

    def encoder_left_callback(self):
        self.hue_values[self.current_index] = (self.hue_values[self.current_index] - 1) % 360
        self.update_leds()

    def encoder_right_callback(self):
        self.hue_values[self.current_index] = (self.hue_values[self.current_index] + 1) % 360
        self.update_leds()

    def green_button_callback(self):
        print("hue_values: ", self.hue_values)
        if self.current_index < len(self.hue_values) - 1:
            self.current_index += 1
            self.update_leds()
        else:
            self.confirm_callback()

    def red_button_callback(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_leds()
            
    def assign_confirm_callback(self, callback):
        self.confirm_callback = callback

    def run(self):
        self.pixels.fill((0, 0, 0))
        self.pixels.show()
        self.current_index = 0
        self.hue_values = [0] * 8
        self.update_leds()
        self.running = True
        print("Rozpoczęcie testu blokady")
        while self.running:
            time.sleep(0.1)
        print("Koniec testu blokady")
        self.pixels.fill((0, 0, 0))
        self.pixels.show()

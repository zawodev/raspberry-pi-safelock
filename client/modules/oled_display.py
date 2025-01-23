# oled_display.py

from PIL import Image
import modules.lib.oled.SSD1331 as SSD1331

display = SSD1331.SSD1331()
display.Init()
display.clear()

def display_image(image):
    display.ShowImage(image, 0, 0)

def display_image_from_path(image_path):
    #display.clear()
    image = Image.open(image_path).resize((96, 64))
    display.ShowImage(image, 0, 0)

def display_text(text):
    display.clear()
    display.text(text, 0, 0)

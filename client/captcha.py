import time

from PIL import Image, ImageOps
import numpy as np
from modules.oled_display import display_image


class Captcha:
    def __init__(self, image_path="/home/pi/tests/mini-project/client/modules/lib/oled/catpcha.png", missing_piece_size=(20, 20), canvas_size=(96, 64)):
        self.image_path = image_path
        self.missing_piece_size = missing_piece_size
        self.canvas_size = canvas_size
        self.axis = 'x'
        self.offset = [0, 0]
        self.original_position = None
        self.base_image, self.missing_piece, self.masked_image = self._prepare_images()
        self.running = False

    def _prepare_images(self):
        image = Image.open(self.image_path).convert("RGB")
        image = image.resize(self.canvas_size)

        # create the missing piece
        x = np.random.randint(0, (self.canvas_size[0] - self.missing_piece_size[0]) / 2)
        y = np.random.randint(0, (self.canvas_size[1] - self.missing_piece_size[1]) / 2)
        self.original_position = (x, y)

        image_array = np.array(image)
        piece = image_array[y:y + self.missing_piece_size[1], x:x + self.missing_piece_size[0]].copy()

        # create a masked version of the image
        masked_image = image_array.copy()
        masked_image[y:y + self.missing_piece_size[1], x:x + self.missing_piece_size[0]] = [0, 0, 0]  # make the piece black

        # add white border around the black square
        masked_image[y:y + self.missing_piece_size[1], x] = [255, 255, 255]  # left border
        masked_image[y:y + self.missing_piece_size[1], x + self.missing_piece_size[0] - 1] = [255, 255, 255]  # right border
        masked_image[y, x:x + self.missing_piece_size[0]] = [255, 255, 255]  # top border
        masked_image[y + self.missing_piece_size[1] - 1, x:x + self.missing_piece_size[0]] = [255, 255, 255]  # bottom border

        return image, piece, Image.fromarray(masked_image)

    def translate_piece(self, delta):
        if self.axis == 'x':
            self.offset[0] = max(0, min(self.offset[0] + delta, self.canvas_size[0] - self.missing_piece_size[0] - 4))
        elif self.axis == 'y':
            self.offset[1] = max(0, min(self.offset[1] + delta, self.canvas_size[1] - self.missing_piece_size[1] - 4))
        self.update_display()

    def switch_axis(self):
        self.axis = 'y' if self.axis == 'x' else 'x'

    def confirm_position(self):
        tolerance = 2  # allowable margin of error in pixels
        original_x, original_y = self.original_position

        if abs(original_x - self.offset[0] - 2) <= tolerance and abs(original_y - self.offset[1] - 2) <= tolerance:
            print("Captcha solved correctly!")
            return True
        else:
            print("Captcha failed!")
            return False

    def get_combined_image(self):
        combined_image = np.array(self.masked_image).copy()
        x, y = self.offset
        piece_with_border = self._add_border_to_piece()
        piece_h, piece_w = piece_with_border.size
        combined_image[y:y + piece_h, x:x + piece_w] = np.array(piece_with_border)
        return Image.fromarray(combined_image)

    def _add_border_to_piece(self):
        # add a black and white border to the missing piece
        piece_image = Image.fromarray(self.missing_piece)
        piece_with_border = ImageOps.expand(piece_image, border=1, fill=(255, 255, 255))  # white border
        piece_with_border = ImageOps.expand(piece_with_border, border=1, fill=(0, 0, 0))  # black border
        return piece_with_border

    def update_display(self):
        combined_image = self.get_combined_image()
        display_image(combined_image)
        
    def run(self):
        self.axis = 'x'
        self.offset = [0, 0]
        self.original_position = None
        self.base_image, self.missing_piece, self.masked_image = self._prepare_images()
        
        self.running = True
        self.update_display()
        while self.running:
            time.sleep(0.1)

from tkinter import colorchooser
import customtkinter as ctk
import colorsys
import math

def rgb_to_hue(r, g, b):
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0
    
    h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)
    
    hue_degrees = h * 360.0

    return math.floor(hue_degrees)


def pick_color_factory(entry_widget):
    def pick_color():
        color_code = colorchooser.askcolor(title="Wybierz kolor")
        if color_code and color_code[0]:
            r, g, b = color_code[0]
            hue = rgb_to_hue(r, g, b)
            entry_widget.delete(0, ctk.END)
            entry_widget.insert(0, str(hue))
    return pick_color


def compare(safe_code, code):
    margin = 50
    if len(safe_code) != len(code) or len(safe_code) != 8:
        return False
    
    def is_in_range(base, target):
        upper_bound = (base + margin) % 360
        lower_bound = (base - margin) % 360
        
        # if the range does not wrap around 0
        if lower_bound <= upper_bound:
            return lower_bound <= target <= upper_bound
        else:
            return target >= lower_bound or target <= upper_bound
            
    return all(is_in_range(val1, val2) for val1, val2 in zip(safe_code, code))
        

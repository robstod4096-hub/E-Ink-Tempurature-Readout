import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont

# Point Python to the 'lib' folder inside the cloned repo
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
from waveshare_epd import epd2in13b_V4  # Use 'bc' for Black/Color (Red/Yellow) models

try:
    # Initialize the display
    epd = epd2in13b_V4.EPD()
    epd.init()
    epd.Clear()

    # Create two blank images matching the screen resolution (e.g., 212x104)
    # 0 = Consume/Draw pixel, 255 = White/Background pixel
    img_black = Image.new('1', (epd.width, epd.height), 255)
    img_color = Image.new('1', (epd.width, epd.height), 255)
    
    draw_black = ImageDraw.Draw(img_black)
    draw_color = ImageDraw.Draw(img_color)

    # 1. Draw something in Black
    draw_black.rectangle((10, 10, 50, 50), fill=0)
    draw_black.text((60, 15), "Black Text", fill=0)

    # 2. Draw something in Red/Yellow
    draw_color.chord((110, 10, 150, 50), 0, 360, fill=0)
    draw_color.text((60, 35), "Colored Text", fill=0)

    # Push both layers to the display (Rotated if layout requires)
    epd.display(epd.getbuffer(img_black), epd.getbuffer(img_color))
    
    print("Refresh complete. Putting screen to sleep...")
    epd.sleep()

except IOError as e:
    print(e)
except KeyboardInterrupt:
    epd2in13b_V4.epdconfig.module_exit()
    exit()

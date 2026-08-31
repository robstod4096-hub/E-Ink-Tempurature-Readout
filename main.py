import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont
from bme280_sensor import read_sensor_data

# Point Python to the 'lib' folder inside the cloned repo
sys.path.append(os.path.join(os.path.dirname(__file__), 'e-Paper/RaspberryPi_JetsonNano/python/lib'))
from waveshare_epd import epd2in13b_V4

epd = epd2in13b_V4.EPD()
epd.init()
epd.Clear()
image = Image.new('1', (epd.width, epd.height), 255)
draw = ImageDraw.Draw(image)

while True:
        epd.init()
        draw.text((60, 15), read_sensor_data()['temperature_fahrenheit'], font=font, fill=0)
        epd.sleep()
        time.sleep(60)  # Update every 60 seconds
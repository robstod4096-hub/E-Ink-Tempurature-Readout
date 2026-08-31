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
        temperature_fahrenheit = read_sensor_data()['temperature_fahrenheit']
        temperature_celsius = read_sensor_data()['temperature_celsius']
        pressure = read_sensor_data()['pressure']
        humidity = read_sensor_data()['humidity']
        draw.rectangle((0, 0, epd.width, epd.height), fill=255)  # Clear the image
        draw.text((10, 10), f"Temperature: {temperature_celsius:.2f} °C / {temperature_fahrenheit:.2f} °F", fill=0)
        draw.text((10, 30), f"Pressure: {pressure:.2f} hPa", fill=0)
        draw.text((10, 50), f"Humidity: {humidity:.2f} %", fill=0)
        epd.display(epd.getbuffer(image))
        epd.sleep()
        time.sleep(60)  # Update every 60 seconds
import os
import sys
import time
from gpiozero import Button
from PIL import Image, ImageDraw, ImageFont
from bme280_sensor import read_sensor_data

# Point Python to the 'lib' folder inside the cloned repo
sys.path.append(os.path.join(os.path.dirname(__file__), 'e-Paper/RaspberryPi_JetsonNano/python/lib'))
from waveshare_epd import epd2in13b_V4

# Initialize the display and clear it
epd = epd2in13b_V4.EPD()
epd.init()
epd.Clear()
image_black = Image.new('1', (epd.height, epd.width), 255)
image_red = Image.new('1', (epd.height, epd.width), 255)
draw = ImageDraw.Draw(image_black)

# Initialize button on pin 36 (GPIO 16)
button = Button(16)

def update_display():
                        # Wake up display
                        epd.init()
        
                        # Retrieve atmospheric data from sensor
                        temperature_fahrenheit = read_sensor_data()['temperature_fahrenheit']
                        temperature_celsius = read_sensor_data()['temperature_celsius']
                        pressure = read_sensor_data()['pressure']
                        humidity = read_sensor_data()['humidity']
        
                        # Draw data on canvas
                        draw.rectangle((0, 0, epd.height, epd.width), fill=255)
                        draw.text((10, 10), f"Temperature: {temperature_celsius:.2f} °C / {temperature_fahrenheit:.2f} °F", fill=0)
                        draw.text((10, 30), f"Pressure: {pressure:.2f} hPa", fill=0)
                        draw.text((10, 50), f"Humidity: {humidity:.2f} %", fill=0)
                        image_black_rotated = image_black.rotate(90, expand=True)
                        image_red_rotated = image_red.rotate(90, expand=True)
        
                        # Push canvas to display
                        epd.display(
                                epd.getbuffer(image_black_rotated), 
                                epd.getbuffer(image_red_rotated)
                                )
        
                        # Put screen to sleep and wait to run again
                        epd.sleep()

while True:
        update_display()
        for i in range(900):
                if button.ispressed():
                        update_display()
                        time.sleep(1)
                else:
                        time.sleep(1)

import os
import sys
import time
import tomllib
from gpiozero import Button
from PIL import Image, ImageDraw, ImageFont
from bme280_sensor import read_sensor_data

# Point Python to the 'lib' folder inside the cloned repo
sys.path.append(os.path.join(os.path.dirname(__file__), 'e-Paper/RaspberryPi_JetsonNano/python/lib'))
from waveshare_epd import epd2in13b_V4

# Initialize the display and clear it
print("Initializing display...")
epd = epd2in13b_V4.EPD()
epd.init()
epd.Clear()
image_black = Image.new('1', (epd.height, epd.width), 255)
image_red = Image.new('1', (epd.height, epd.width), 255)
draw_black = ImageDraw.Draw(image_black)
draw_red = ImageDraw.Draw(image_red)

# Initialize button on pin 36 (GPIO 16)
button = Button(16)

# Open config file
with open("config.toml", "rb") as f:
    data = tomllib.load(f)

def update_display():
                        print("Updating display...")

                        # Wake up display
                        epd.init()
        
                        # Retrieve atmospheric data from sensor
                        if data["general"]["units"] == "fahrenheit":
                                temperature = read_sensor_data()['temperature_fahrenheit']
                                symbol = "°F"
                        elif data["general"]["units"] == "celsius":
                                temperature = read_sensor_data()['temperature_celsius']
                                symbol = "°C"
                        pressure = read_sensor_data()['pressure']
                        humidity = read_sensor_data()['humidity']
        
                        # Draw data on canvas
                        draw_black.rectangle((0, 0, epd.height, epd.width), fill=255)
                        draw_red.rectangle((123, 0, 128, epd.width), fill="red", outline="black")
                        draw_black.text((5, 10), f"Temperature: {temperature:.2f} {symbol}", fill=0)
                        draw_black.text((5, 30), f"Pressure: {pressure:.2f} hPa", fill=0)
                        draw_black.text((5, 50), f"Humidity: {humidity:.2f} %", fill=0)

                        # Rotate canvas from portrait to landscape
                        image_black_rotated = image_black.rotate(90, expand=True)
                        image_red_rotated = image_red.rotate(90, expand=True)
        
                        # Push canvas to display
                        epd.display(
                                epd.getbuffer(image_black_rotated), 
                                epd.getbuffer(image_red_rotated),
                                )
        
                        # Put screen to sleep and wait to run again
                        epd.sleep()

while True:
        update_display()
        time_remaining = data["general"]["update_interval"]
        for i in range(data["general"]["update_interval"]):
                if button.is_pressed:
                        update_display()
                        time.sleep(1)
                else:
                        time.sleep(1)
                time_remaining -= 1
                print(f"Time remaining until next update: {time_remaining} seconds", end="\r")

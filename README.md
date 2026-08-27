# E-Ink-Tempurature-Readout
A simple project that displays the room tempurature and and the outside weather.

To set up BME280:
- Run "sudo raspi-config"
- Select interface options
- Select and enable I2C
- Reboot the pi
- Run "sudo i2cdetect -y 1"
- Verify that the BME280 sensor address is 0x76
- If not change the variable in bme280_sensor.py

To set up MH-ET LIVE E-ink display:
- Run "sudo raspi-config"
- Select interface options
- Select and enable SPIimport os
import sys
import time
from PIL import Image, ImageDraw, ImageFont

# Point Python to the 'lib' folder inside the cloned repo
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
from tp_epd import epd2in13bc  # Use 'bc' for Black/Color (Red/Yellow) models

try:
    # Initialize the display
    epd = epd2in13bc.EPD()
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
    epd2in13bc.epdconfig.module_exit()
    exit()

Use code with caution.
📌 Hardware Pin Connection Guide
- Reboot the pi
- Run "sudo apt update", "sudo apt install -y git python3-pip python3-pil python3-numpy", "sudo pip3 install rpi.gpio spidev --break-system-packages"
- Run "git clone https://github.com"
- Run "cd e-Paper/RaspberryPi_JetsonNano/python"
- Move test_epd.py into this directory
- Run test_epd.py to test the screen
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
- Select and enable SPI
- Reboot the pi
- Run "sudo apt update", "sudo apt install -y git python3-pip python3-pil python3-numpy", "sudo pip3 install rpi.gpio spidev --break-system-packages"
- Run "git clone https://github.com"
- Run "cd e-Paper/RaspberryPi_JetsonNano/python"
- Move test_epd.py into this directory
- Run test_epd.py to test the screen
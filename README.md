# E-Ink-Tempurature-Readout
A simple project that displays the room tempurature and and the outside weather.

To set up:
- Run "sudo raspi-config"
- Select interface options
- Select and enable I2C and SPI
- Reboot the pi
- Run "sudo i2cdetect -y 1"
- Verify that the BME280 sensor address is 0x76
- If not change the variable in bme280_sensor.py
"""
bme280_sensor.py - Indoor Environmental Sensor Module
-----------------------------------------------------
Reads temperature, humidity, and barometric pressure from the BME280
sensor via I2C bus using CircuitPython/Adafruit libraries.
"""

import time
import board
import busio
import adafruit_bme280.advanced as adafruit_bme280

import config


class BME280Sensor:
    def __init__(self, i2c_address=config.BME280_I2C_ADDRESS):
        """Initializes the I2C bus and BME280 sensor instance."""
        self.i2c_address = i2c_address
        self.sensor = None
        self._init_sensor()

    def _init_sensor(self):
        """Attempts to initialize the BME280 sensor over I2C."""
        try:
            # Initialize I2C bus on Pi GPIO 2 (SDA) / GPIO 3 (SCL)
            i2c = busio.I2C(board.SCL, board.SDA)
            self.sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=self.i2c_address)
            
            # Optional: Set sea level pressure for altitude calculations if needed
            self.sensor.sea_level_pressure = 1013.25
            print(f"BME280 sensor successfully initialized at address 0x{self.i2c_address:02X}")
        except Exception as error:
            print(f"Error initializing BME280 sensor at 0x{self.i2c_address:02X}: {error}")
            self.sensor = None

    def read_data(self):
        """
        Reads raw data from the sensor and converts units based on config.UNITS.
        
        Returns:
            dict: {
                'temperature': float,
                'humidity': float,
                'pressure': float,
                'status': bool
            }
        """
        # Retry initialization once if sensor failed during boot
        if self.sensor is None:
            self._init_sensor()

        if self.sensor is None:
            print("Unable to read BME280: Sensor not connected or initialized.")
            return {
                "temperature": 0.0,
                "humidity": 0.0,
                "pressure": 0.0,
                "status": False
            }

        try:
            temp_c = self.sensor.temperature
            humidity = self.sensor.humidity
            pressure_hpa = self.sensor.pressure

            # Convert units based on config settings
            if config.UNITS.lower() == "imperial":
                temp = (temp_c * 9.0 / 5.0) + 32.0  # Celsius to Fahrenheit
                pressure = pressure_hpa * 0.02953    # hPa to inHg
            else:
                temp = temp_c                         # Celsius
                pressure = pressure_hpa               # hPa

            return {
                "temperature": round(temp, 1),
                "humidity": round(humidity, 1),
                "pressure": round(pressure, 1),
                "status": True
            }

        except Exception as error:
            print(f"Failed to read data from BME280: {error}")
            return {
                "temperature": 0.0,
                "humidity": 0.0,
                "pressure": 0.0,
                "status": False
            }


# ==========================================
# STANDALONE TEST RUNNER
# ==========================================
if __name__ == "__main__":
    print("Testing BME280 Sensor...")
    bme = BME280Sensor()
    
    # Take a reading
    data = bme.read_data()
    
    if data["status"]:
        unit_temp = "°F" if config.UNITS == "imperial" else "°C"
        unit_press = "inHg" if config.UNITS == "imperial" else "hPa"
        
        print("\n--- BME280 Reading Success ---")
        print(f"Temperature : {data['temperature']}{unit_temp}")
        print(f"Humidity    : {data['humidity']}%")
        print(f"Pressure    : {data['pressure']} {unit_press}")
    else:
        print("\nFailed to get valid sensor readings. Check wiring and i2cdetect.")
import smbus2
import bme280

# BME280 sensor address (default address)
address = 0x76

# Initialize I2C bus
bus = smbus2.SMBus(1)

# Load calibration parameters
calibration_params = bme280.load_calibration_params(bus, address)

def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def read_sensor_data():
    # Read sensor data
    data = bme280.sample(bus, address, calibration_params)
    
    # Extract temperature, pressure, and humidity
    temperature_celsius = data.temperature
    pressure = data.pressure
    humidity = data.humidity
    
    # Convert temperature to Fahrenheit
    temperature_fahrenheit = celsius_to_fahrenheit(temperature_celsius)

    # Return data as a dictionary
    return {
        "temperature_celsius": temperature_celsius,
        "temperature_fahrenheit": temperature_fahrenheit,
        "pressure": pressure,
        "humidity": humidity
    }
import os

USER_AGENT_EMAIL = "robstod4096@gmail.com"
NWS_USER_AGENT = f"RPi-ePaperWeatherStation/1.0 ({USER_AGENT_EMAIL})"
UNITS = "imperial"
WEATHER_LANG = "en"

AUTO_LOCATION_FROM_IP = True
DEFAULT_LATITUDE = 40.2338
DEFAULT_LONGITUDE = -111.6585
DEFAULT_CITY_NAME = "Provo"

NETWORK_TIMEOUT = 10

# BME280 Indoor Sensor (I2C)
I2C_BUS = 1
BME280_I2C_ADDRESS = 0x76  # Default address (0x76 or 0x77)

# SPI Display Control Pins (BCM GPIO Numbering)
EPD_RST_PIN = 17   # Reset pin (Physical Pin 11)
EPD_DC_PIN = 25    # Data/Command pin (Physical Pin 22)
EPD_CS_PIN = 8     # SPI Chip Select 0 (Physical Pin 24)
EPD_BUSY_PIN = 24  # Busy Status pin (Physical Pin 18)

# Physical Push-Button (Momentary Tactile Switch)
BUTTON_GPIO_PIN = 16  # Active LOW using internal pull-up (Physical Pin 36)
BUTTON_DEBOUNCE_TIME = 0.2  # Bounce time in seconds to prevent accidental double-clicks

# E-Paper Screen Resolution (Adjust to match specific vendor model)
DISPLAY_WIDTH = 212
DISPLAY_HEIGHT = 104

# Rotation of the display canvas: 0, 90, 180, or 270 degrees
DISPLAY_ROTATION = 0

COLOR_WHITE  = (255, 255, 255)
COLOR_BLACK  = (0, 0, 0)
COLOR_RED    = (255, 0, 0)
COLOR_YELLOW = (255, 220, 0)

# 4-color e-Paper displays CANNOT perform partial refreshes
ENABLE_PARTIAL_REFRESH = False

# Automated Background Update Schedule (in seconds)
# 900 seconds = 15 Minutes
UPDATE_INTERVAL_SECONDS = 900

# Perform a full screen refresh (flashes black/white) every N updates to clear ghosting
FULL_REFRESH_FREQUENCY = 4

# Base Directory of the Project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Assets Directories
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")

# TTF Font Paths
FONT_LARGE_PATH = os.path.join(FONTS_DIR, "Roboto-Bold.ttf")
FONT_SMALL_PATH = os.path.join(FONTS_DIR, "Roboto-Regular.ttf")
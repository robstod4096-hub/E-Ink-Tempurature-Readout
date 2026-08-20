"""
main.py - Main Application Controller
-------------------------------------
Coordinates BME280 sensor reads, OpenWeatherMap API fetches, Pillow canvas
rendering, physical button interrupts, and SPI e-Paper display updates.
"""

import time
import sys
import signal
import threading

# Import custom project modules
import config
from bme280_sensor import BME280Sensor
from weather_api import WeatherAPI
from renderer import DisplayRenderer

# Import the 4-color EPD driver module
try:
    from waveshare_epd import epd2in13_4color as epd_driver
except ImportError:
    import epd_driver  # Or your local MH-ET LIVE driver module

# Import button control library
try:
    from gpiozero import Button
except ImportError:
    Button = None


class WeatherStationApp:
    def __init__(self):
        print("Initializing Weather Station Application...")
        
        # 1. Initialize Subsystems
        self.sensor = BME280Sensor()
        self.weather_api = WeatherAPI()
        self.renderer = DisplayRenderer()
        
        # 2. State & Concurrency Controls
        self.refresh_lock = threading.Lock()
        self.update_count = 0
        self.running = True
        
        # 3. Initialize Display Driver
        self.epd = None
        if epd_driver:
            try:
                self.epd = epd_driver.EPD()
                print("E-Paper display driver loaded successfully.")
            except Exception as err:
                print(f"Failed to instantiate e-Paper driver: {err}")
        else:
            print("WARNING: Waveshare e-Paper driver not found. Running in headless mode.")

        # 4. Initialize Push Button Interrupt (GPIO 16)
        self.button = None
        if Button:
            try:
                self.button = Button(
                    config.BUTTON_GPIO_PIN, 
                    pull_up=True, 
                    bounce_time=config.BUTTON_DEBOUNCE_TIME
                )
                self.button.when_pressed = self.trigger_manual_refresh
                print(f"Push button listener registered on GPIO {config.BUTTON_GPIO_PIN}.")
            except Exception as err:
                print(f"Failed to initialize GPIO button: {err}")

    def update_display(self, force_full_refresh=True):
        if not self.refresh_lock.acquire(blocking=False):
            return

        try:
            indoor_data = self.sensor.read_data()
            outdoor_data = self.weather_api.fetch_weather()

            # Render RGB Image
            image_canvas = self.renderer.create_canvas(indoor_data, outdoor_data)

            if self.epd:
                print("Initiating 4-color display refresh (~15-20s execution)...")
                self.epd.init()
                
                # The 4-color driver handles converting the RGB canvas 
                # into the screen's internal 4-color buffer format
                self.epd.display(self.epd.getbuffer(image_canvas))
                
                self.epd.sleep()
                print("Update complete. Display in sleep mode.")
            else:
                image_canvas.save("latest_preview.png")

        finally:
            self.refresh_lock.release()

    def trigger_manual_refresh(self):
        """Callback handler triggered when the physical push button is pressed."""
        print("\n[BUTTON] Manual refresh requested via GPIO button!")
        # Force a full refresh on button press to guarantee clean output
        threading.Thread(target=self.update_display, kwargs={"force_full_refresh": True}).start()

    def cleanup(self, signum=None, frame=None):
        """Gracefully shuts down hardware SPI and GPIO interface."""
        print("\nShutting down Weather Station Application...")
        self.running = False
        if self.epd:
            try:
                print("Cleaning up e-Paper display GPIO state...")
                self.epd.init()
                self.epd.Clear()
                self.epd.sleep()
            except Exception as err:
                print(f"Error putting display to sleep: {err}")
        sys.exit(0)

    def run(self):
        """Main execution loop for scheduled updates."""
        # Attach OS process signals (Ctrl+C, systemctl stop) to cleanup handler
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)

        # Execute initial display render on startup
        self.update_display(force_full_refresh=True)

        print(f"\nSystem active. Automated updates scheduled every {config.UPDATE_INTERVAL_SECONDS} seconds.")
        print("Press Ctrl+C to terminate application gracefully.")

        # Background Loop
        last_update_time = time.time()
        while self.running:
            current_time = time.time()
            # Check if scheduled interval has elapsed
            if current_time - last_update_time >= config.UPDATE_INTERVAL_SECONDS:
                self.update_display(force_full_refresh=False)
                last_update_time = time.time()
            
            # Idle sleep to minimize CPU usage
            time.sleep(1)


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================
if __name__ == "__main__":
    app = WeatherStationApp()
    app.run()
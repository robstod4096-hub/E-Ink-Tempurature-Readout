"""
renderer.py - Pillow Display Canvas Renderer
-------------------------------------------
Combines indoor BME280 sensor data and outdoor weather API data onto
a 1-bit black-and-white image buffer for e-Paper displays.
"""

import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

import config


class DisplayRenderer:
    def __init__(self, width=config.DISPLAY_WIDTH, height=config.DISPLAY_HEIGHT):
        self.width = width
        self.height = height
        self.unit_symbol = "°F" if config.UNITS.lower() == "imperial" else "°C"
        
        # Load fonts (falls back to default bitmap font if custom TTF is missing)
        self.font_large = self._load_font(config.FONT_LARGE_PATH, size=24)
        self.font_medium = self._load_font(config.FONT_LARGE_PATH, size=16)
        self.font_small = self._load_font(config.FONT_SMALL_PATH, size=11)
        self.font_tiny = self._load_font(config.FONT_SMALL_PATH, size=9)

    def _load_font(self, path, size):
        """Attempts to load a TTF font; falls back to default if unavailable."""
        try:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
        except Exception as err:
            print(f"Warning loading font {path}: {err}")
        return ImageFont.load_default()

    def _draw_weather_symbol(self, draw, x, y, icon_code):
        """Draws simple geometric icons directly on the canvas for weather types."""
        # Simple procedural graphics for e-Paper when icons are missing
        if "01" in icon_code:  # Clear / Sun
            draw.ellipse((x, y, x + 16, y + 16), outline=0, width=2)
        elif "02" in icon_code or "03" in icon_code or "04" in icon_code:  # Clouds
            draw.ellipse((x, y + 4, x + 12, y + 14), outline=0, fill=255)
            draw.ellipse((x + 6, y, x + 18, y + 14), outline=0, fill=255)
            draw.ellipse((x + 10, y + 6, x + 22, y + 14), outline=0, fill=255)
            draw.line((x + 2, y + 14, x + 20, y + 14), fill=0, width=2)
        elif "09" in icon_code or "10" in icon_code:  # Rain
            draw.ellipse((x, y, x + 16, y + 10), outline=0, fill=255)
            draw.line((x + 3, y + 12, x + 1, y + 16), fill=0, width=2)
            draw.line((x + 8, y + 12, x + 6, y + 16), fill=0, width=2)
            draw.line((x + 13, y + 12, x + 11, y + 16), fill=0, width=2)
        else:  # Generic fallback box
            draw.rectangle((x, y, x + 16, y + 16), outline=0, width=1)

    def create_canvas(self, indoor_data, outdoor_data):
        """
        Generates an RGB PIL Image canvas for 4-color e-Paper (Black, White, Red, Yellow).
        """
        # 1. Create blank WHITE canvas in RGB mode
        image = Image.new("RGB", (self.width, self.height), config.COLOR_WHITE)
        draw = ImageDraw.Draw(image)

        # 2. HEADER BAR (Red background with White text)
        draw.rectangle((0, 0, self.width, 16), fill=config.COLOR_RED)
        draw.text((4, 2), "HOME WEATHER", font=self.font_small, fill=config.COLOR_WHITE)
        
        time_str = datetime.now().strftime("%H:%M")
        draw.text((self.width - 32, 2), time_str, font=self.font_small, fill=config.COLOR_WHITE)

        # 3. DIVIDERS & FRAMES (Black)
        mid_x = self.width // 2
        draw.line((mid_x, 16, mid_x, self.height - 14), fill=config.COLOR_BLACK, width=1)
        draw.line((0, self.height - 14, self.width, self.height - 14), fill=config.COLOR_BLACK, width=1)

        # 4. INDOOR SECTION
        draw.text((6, 20), "INDOOR", font=self.font_tiny, fill=config.COLOR_BLACK)
        if indoor_data.get("status", False):
            temp_in = f"{indoor_data['temperature']}{self.unit_symbol}"
            # Highlight indoor temperature in BLACK
            draw.text((6, 32), temp_in, font=self.font_large, fill=config.COLOR_BLACK)
            draw.text((6, 62), f"Hum: {indoor_data['humidity']}%", font=self.font_small, fill=config.COLOR_BLACK)
            draw.text((6, 78), f"{indoor_data['pressure']} hPa", font=self.font_tiny, fill=config.COLOR_BLACK)
        else:
            draw.text((6, 40), "Sensor Error", font=self.font_small, fill=config.COLOR_RED)

        # 5. OUTDOOR SECTION
        out_x = mid_x + 6
        city_name = outdoor_data.get("city", "OUTDOOR")[:12].upper()
        draw.text((out_x, 20), city_name, font=self.font_tiny, fill=config.COLOR_BLACK)

        if outdoor_data.get("status", False):
            temp_out = f"{outdoor_data['temperature']}{self.unit_symbol}"
            
            # Highlight outdoor temperature in YELLOW or RED based on conditions
            temp_color = config.COLOR_RED if outdoor_data['temperature'] > 25 else config.COLOR_YELLOW
            
            self._draw_weather_symbol(draw, out_x, 36, outdoor_data.get("icon_code", "01d"))
            draw.text((out_x + 24, 32), temp_out, font=self.font_medium, fill=temp_color)
            draw.text((out_x, 62), outdoor_data.get("description", "N/A")[:15], font=self.font_tiny, fill=config.COLOR_BLACK)
            draw.text((out_x, 78), f"Hum: {outdoor_data['humidity']}%", font=self.font_small, fill=config.COLOR_BLACK)

        # 6. FOOTER
        draw.text((4, self.height - 12), datetime.now().strftime("%b %d, %Y"), font=self.font_tiny, fill=config.COLOR_BLACK)

        if config.DISPLAY_ROTATION != 0:
            image = image.rotate(config.DISPLAY_ROTATION, expand=True)

        return image

# ==========================================
# STANDALONE TEST RUNNER (LOCAL PREVIEW)
# ==========================================
if __name__ == "__main__":
    print("Testing Display Renderer...")
    renderer = DisplayRenderer()

    # Mock Data
    mock_indoor = {
        "temperature": 21.5,
        "humidity": 42.0,
        "pressure": 1013.2,
        "status": True
    }

    mock_outdoor = {
        "temperature": 18.2,
        "humidity": 65,
        "description": "Light Rain",
        "icon_code": "10d",
        "city": "Provo",
        "status": True
    }

    # Generate Image Canvas
    canvas = renderer.create_canvas(mock_indoor, mock_outdoor)

    # Save to local file so you can inspect the layout visually
    output_filename = "preview.png"
    canvas.save(output_filename)
    print(f"Canvas layout generated successfully! Saved preview image to '{output_filename}'.")
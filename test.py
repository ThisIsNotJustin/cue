import math
import asyncio
from bleak import BleakClient, BleakScanner

## Device information
MAC = "C7:46:23:94:4A:14"
POWER_UUID = "932c32bd-0002-47a2-835a-a8d455b859dd"
BRIGHTNESS_UUID = "932c32bd-0003-47a2-835a-a8d455b859dd"
TEMP_UUID = "932c32bd-0004-47a2-835a-a8d455b859dd"
COLOR_UUID = "932c32bd-0005-47a2-835a-a8d455b859dd"

## Color Gamut C triangle vertices for Philips Hue (newer models)
RED = {"x": 0.6915, "y": 0.3038}
GREEN = {"x": 0.17, "y": 0.7}
BLUE = {"x": 0.1532, "y": 0.0475}

class XyPoint:
    def __init__(self, x, y, brightness=None):
        self.x = x
        self.y = y
        self.brightness = brightness
    
    def within_gamut(self):
        x, y = self.x, self.y
        x1, y1 = RED["x"], RED["y"]
        x2, y2 = GREEN["x"], GREEN["y"]
        x3, y3 = BLUE["x"], BLUE["y"]
        
        denominator = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        
        lambda1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / denominator
        lambda2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / denominator
        lambda3 = 1 - lambda1 - lambda2
        
        return (0 <= lambda1 <= 1) and (0 <= lambda2 <= 1) and (0 <= lambda3 <= 1)
    
    def euclidean_distance(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    
    def point_to_segment(self, a, b):
        ab_x = b.x - a.x
        ab_y = b.y - a.y
        
        ap_x = self.x - a.x
        ap_y = self.y - a.y
        
        t = (ap_x * ab_x + ap_y * ab_y) / (ab_x * ab_x + ab_y * ab_y)
        t = max(0, min(1, t))
        
        return XyPoint(a.x + t * ab_x, a.y + t * ab_y)
    
    def point_in_triangle(self):
        ## If a value doesn't fall within the color gamut capable of the bulb
        ## We need to find the closest point in the gamut triangle
        x1 = XyPoint(RED["x"], RED["y"])
        x2 = XyPoint(GREEN["x"], GREEN["y"])
        x3 = XyPoint(BLUE["x"], BLUE["y"])
        
        p1_closest = self.point_to_segment(x1, x2)
        p2_closest = self.point_to_segment(x2, x3)
        p3_closest = self.point_to_segment(x3, x1)
        
        d1 = self.euclidean_distance(p1_closest)
        d2 = self.euclidean_distance(p2_closest)
        d3 = self.euclidean_distance(p3_closest)
        
        if d1 < d2 and d1 < d3:
            return p1_closest
        elif d2 < d1 and d2 < d3:
            return p2_closest
        else:
            return p3_closest

## https://developers.meethue.com/develop/application-design-guidance/color-conversion-formulas-rgb-to-xy-and-back/#Gamut
def rgb_to_xy(r, g, b):
    ## All of this is pretty much from the devloper documentation
    ## Normalize RGB values to 0-1
    r = r / 255
    g = g / 255
    b = b / 255
    
    ## Apply gamma correction from hue documentation
    r = (r / 12.92) if r <= 0.04045 else ((r + 0.055) / (1.0 + 0.055)) ** 2.4
    g = (g / 12.92) if g <= 0.04045 else ((g + 0.055) / (1.0 + 0.055)) ** 2.4
    b = (b / 12.92) if b <= 0.04045 else ((b + 0.055) / (1.0 + 0.055)) ** 2.4
    
    ## Convert to XYZ with formula from hue documentation
    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505
    
    ## Convert to xy
    brightness = y
    try:
        x_chroma = x / (x + y + z)
        y_chroma = y / (x + y + z)
    except ZeroDivisionError:
        ## Handle black (0,0,0)
        x_chroma = 0
        y_chroma = 0
    
    xy = XyPoint(x_chroma, y_chroma, brightness)
    
    ## Ensure the point is within the color gamut
    if not xy.within_gamut():
        xy = xy.point_in_triangle()
    
    return xy, brightness


class HueBleController:
    def __init__(self, address):
        self.address = address
        self.client = None
    
    async def connect(self):
        print(f"Connecting to {self.address}...")
        self.client = BleakClient(self.address)
        await self.client.connect()

        if self.client.is_connected:
            print(f"Connected to {self.address}")
            return True
        else:
            print(f"Failed to connect to {self.address}")
            return False
    
    async def disconnect(self):
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print(f"Disconnected from {self.address}")
    
    async def power_on(self):
        await self.client.write_gatt_char(POWER_UUID, bytearray([0x01]))
        print("Light turned on")
    
    async def power_off(self):
        await self.client.write_gatt_char(POWER_UUID, bytearray([0x00]))
        print("Light turned off")
    
    async def set_brightness(self, brightness_percent):
        brightness_value = int(min(max(brightness_percent, 0), 100) * 255 / 100)
        await self.client.write_gatt_char(BRIGHTNESS_UUID, bytearray([brightness_value]))
        print(f"Brightness set to {brightness_percent}%")
    
    async def set_colors_xy(self, x, y):
        ## Hue angle - https://stackoverflow.com/questions/22564187/rgb-to-philips-hue-hsb
        scale_factor = 65535
        scaled_x = int(x * scale_factor)
        scaled_y = int(y * scale_factor)
        
        ## Create buffer for XY values (4 bytes: 2 for x, 2 for y)
        buffer = bytearray(4)
        buffer[0] = scaled_x & 0xFF
        buffer[1] = (scaled_x >> 8) & 0xFF
        buffer[2] = scaled_y & 0xFF
        buffer[3] = (scaled_y >> 8) & 0xFF
        
        ## print(f"Setting XY color: ({x:.4f}, {y:.4f}) -> scaled: ({scaled_x}, {scaled_y})")
        await self.client.write_gatt_char(COLOR_UUID, buffer)
    
    async def set_colors_rgb(self, r, g, b):
        print(f"Setting RGB color: ({r}, {g}, {b})")
        xy, brightness = rgb_to_xy(r, g, b)
        
        await self.set_colors_xy(xy.x, xy.y)


async def discover_devices():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()

    for d in devices:
        print(f"Found device: {d.name} ({d.address})")
    return devices


async def main():
    controller = HueBleController(MAC)
    
    try:
        connected = await controller.connect()
        if not connected:
            print("Failed to connect. Exiting..")
            return
        
        await controller.power_on()
        await asyncio.sleep(2)
        
        await controller.set_brightness(100)
        await asyncio.sleep(2)
        
        print("Color adjust - blue")
        await controller.set_colors_rgb(0, 0, 255)
        await asyncio.sleep(2)
        
        print("Color adjust - green")
        await controller.set_colors_rgb(0, 255, 0)
        await asyncio.sleep(2)
        
        print("Color adjust - yellow")
        await controller.set_colors_rgb(255, 255, 0)
        await asyncio.sleep(2)

        await controller.power_off()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await controller.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
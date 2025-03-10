"""
    Hue BLE firmware testing
    Mainly attempting to understand the RGB control

    1st Header - 0 = does not write
                - 254 (non zero) = writes values
    
    2nd Header - 0 = potentially blue but more on that
                - 254 = red but more on that

    3rd Header - 0 = sometimes saturation control, 254, 254, 0 = not red
                - 254 = sometimes saturation control, 254, 254, 254 = red
    
    4th Header - 0 = no green, can make cyan IFF 2nd headers 0
                - 254 = green


    So 1st is blue -> red
    4th is like an override mode? and it controls cyan -> green

    This code will simply be used to control lights with a rotary encoder
    At the moment thinking: 0 degrees -> 170ish control red -> blue
    170 -> 190ish control cyan -> green
    I currently do not know how to make yellow? or orange?
"""

## Device C7:46:23:94:4A:14 Hue color lamp 2
import asyncio
import math
from bleak import BleakClient

MAC = "C7:46:23:94:4A:14"
POWER_UUID = "932c32bd-0002-47a2-835a-a8d455b859dd"
BRIGHTNESS_UUID = "932c32bd-0003-47a2-835a-a8d455b859dd"
TEMP_UUID = "932c32bd-0004-47a2-835a-a8d455b859dd"
COLOR_UUID = "932c32bd-0005-47a2-835a-a8d455b859dd"

"""
G_RED = (0.6915, 0.3038)
G_GREEN = (0.17, 0.7)
G_BLUE = (0.1532, 0.0475)
"""

# Trying gamut b
G_RED = (0.675, 0.322)
G_GREEN = (0.409, 0.518)
G_BLUE = (0.167, 0.04)

async def set_color_hsv(hue: float, saturation: float, client):
    ## hue: 0-360, saturation: 0-1?
    hue8 = int((hue / 360) * 254)
    sat8 = int(saturation * 254)

    cmd = bytes([0xfe, hue8, sat8, 0x00])
    await client.write_gatt_char(COLOR_UUID, cmd, response=False)

async def control_bulb(addr):
    async with BleakClient(addr) as client:
        if client.is_connected:
            print("Connected to bulb")

            for service in client.services:
                print(f"Service: {service.uuid}")
                for char in service.characteristics:
                    print(f"  Characteristic: {char.uuid}, Properties: {char.properties}")
            
            await client.write_gatt_char(POWER_UUID, b"\x01", response=False)
            print("Bulb on")
            await asyncio.sleep(1)

            ## fe should be 254 im not sure why it didn't work previously but seems full brightness now
            await client.write_gatt_char(BRIGHTNESS_UUID, b"\xfe", response=False)
            print("Brightness set to 100%")
            await asyncio.sleep(2)

            # does nothing atm
            # b"\x04\x00\x00\xfe"
            # bytes([254, 0, 254, 0]) - blue
            # bytes([254, 254, 254, 0]) - red
            # bytes([254, 0, 0, 254]) - green
            # bytes([254, 80, 254, 0]) - purple
            # bytes([254, 140, 254, 0]) - magenta
            cmd = bytes([254, 220, 254, 0])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("Color adjust - Red")
            await asyncio.sleep(2)

            # very warm temp
            temp = 6500 // 10
            cmd = temp.to_bytes(2, byteorder='little')
            await client.write_gatt_char(TEMP_UUID, cmd, response=False)
            print("Warm temp")
            await asyncio.sleep(2)

            # very cool temp
            temp = 2700 // 10
            cmd = temp.to_bytes(2, byteorder='little')
            await client.write_gatt_char(TEMP_UUID, cmd, response=False)
            print("Cold temp")
            await asyncio.sleep(2)

            cmd = bytes([254, 0, 254, 254])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("Green")
            await asyncio.sleep(2)

            cmd = bytes([254, 0, 254, 80])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("4th header adjustment (80)") # a faded cyan - very interesting
            await asyncio.sleep(2)

            cmd = bytes([254, 0, 0, 80])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("3rd header 0 with 4th header at 80") # a faded cyan still so 3rd header does not matter?
            await asyncio.sleep(2)

            cmd = bytes([254, 254, 0, 80])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("2nd header 254, with 4th at 80") # a faded cyan still so 2nd header does not matter???
            await asyncio.sleep(2)

            cmd = bytes([254, 0, 20, 254])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("2nd header back to 0, 3rd header at 20, 4th back to 254") # green, 3rd header has no effect?
            await asyncio.sleep(2)

            cmd = bytes([254, 0, 0, 254])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("Green for comparison") # exactly the same as previous green so confirms 3rd header changes nothing
            await asyncio.sleep(2)

            cmd = bytes([0, 0, 0, 254])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("Header as 0 test") # first header can be 0, produces the same thing
            await asyncio.sleep(2)

            cmd = bytes([100, 0, 0, 254])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("Header as 100 test") # no change
            await asyncio.sleep(2)

            cmd = bytes([180, 0, 0, 254])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("Header as 180 test") # no change
            await asyncio.sleep(2)

            cmd = bytes([10, 0, 0, 254])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("Header as 10 test") # no change
            await asyncio.sleep(2)

            cmd = bytes([254, 254, 254, 254])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("all 254 test") # exactly the same so if 4th header is not 0, all other headers do not matter?
            await asyncio.sleep(2)

            await set_color_hsv(200, 1.0, client)
            print("Magenta") # magenta
            await asyncio.sleep(2)

            await set_color_hsv(360, 0.0, client)
            print("Red hue testing") # magenta color - exactly the same as previous
            await asyncio.sleep(2)

            await set_color_hsv(360, 1.0, client)
            print("Red hue testing pt 2") # red so hue seems to work?
            await asyncio.sleep(2)

            await set_color_hsv(0, 1.0, client)
            print("Blue") # blue
            await asyncio.sleep(2)

            cmd = bytes([0, 0, 0, 0])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("all 0 test") # still blue
            await asyncio.sleep(2)

            cmd = bytes([254, 0, 0, 10])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("254 header 1st, 10 4th header") # still same
            await asyncio.sleep(2)

            cmd = bytes([0, 0, 0, 100])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("1st header 0, 4th 100") # still blue
            await asyncio.sleep(2)

            cmd = bytes([254, 0, 0, 100])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("1st header 254, 4th 100") # changes to a cyan so! 1st header must be nonzero to write a value
            await asyncio.sleep(2)

            cmd = bytes([254, 0, 0, 0])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("1st header 254, all 0 test") # still cyan
            await asyncio.sleep(2)

            cmd = bytes([0, 0, 0, 130])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("1st header 0, 4th 130") # no change so for sure 1st header must be nonzero 
            await asyncio.sleep(2)

            cmd = bytes([254, 0, 0, 130])
            await client.write_gatt_char(COLOR_UUID, cmd, response=False)
            print("1st header 254, 4th 130") # slightly different from previous
            await asyncio.sleep(2)
            
            await client.write_gatt_char(BRIGHTNESS_UUID, b"\x33", response=False)
            print("Brightness set to 20%")
            await asyncio.sleep(2)
            
            await client.write_gatt_char(POWER_UUID, b"\x00", response=False)
            print("Bulb off")
            
        else:
            print("Failed to connect")

async def turn_off(addr):
    async with BleakClient(addr) as client:
        if client.is_connected:
            print("Connected to bulb")

            await client.write_gatt_char(POWER_UUID, b"\x00", response=False)

async def set_color_rgb(r: int, g: int, b: int, client):
    x, y = rgb_xy(r, g, b)
    print(f"Original xy: ({x:.3f}, {y:.3f}) for RGB({r}, {g}, {b})")
    packet = build_color_packet(x, y)
    await client.write_gatt_char(COLOR_UUID, packet, response=False)

def gamma_correct(c):
    return ((c + 0.055) / (1 + 0.055)) ** 2.4 if c > 0.04045 else c / 12.92

def rgb_xy(r: int, g: int, b: int):
    rnorm, gnorm, bnorm = r / 255.0, g / 255.0, b / 255.0
    rcorrect, gcorrect, bcorrect = gamma_correct(rnorm), gamma_correct(gnorm), gamma_correct(bnorm)

    x = rcorrect * 0.4124 + gcorrect * 0.3576 + bcorrect * 0.1805
    y = rcorrect * 0.2126 + gcorrect * 0.7152 + bcorrect * 0.0722
    z = rcorrect * 0.0193 + gcorrect * 0.1192 + bcorrect * 0.9505

    total = x + y + z
    if total == 0:
        return (0.0, 0.0)
    
    x_final = x / total
    y_final = y / total

    return x_final, y_final

def adjust_xy_to_gamut(x: float, y: float):
    p = (x, y)
    a = G_RED
    b = G_GREEN
    c = G_BLUE
    if point_in_triangle(p, a, b, c):
        return p
    else:
        return closest_point_in_triangle(p, a, b, c)

def build_color_packet(x: float, y: float):
    X, Y = adjust_xy_to_gamut(x, y)
    scale_x = int(X * 0xFFFF)
    scale_y = int(Y * 0xFFFF)

    set_bit = 254 # I've tried 0x01, 0xfe (254), idk
    packet = bytes([set_bit]) + scale_x.to_bytes(2, byteorder='little') + scale_y.to_bytes(2, byteorder='little')
    print(f"Adjusted xy: ({X:.3f}, {Y:.3f}), Scaled x: {scale_x}, Scaled y: {scale_y}, Packet: {packet}")

    return packet

def point_in_triangle(p, a, b, c):
    # Using barycentric coordinates to determine if p is inside triangle abc
    (px, py), (ax, ay), (bx, by), (cx, cy) = p, a, b, c
    v0 = (cx - ax, cy - ay)
    v1 = (bx - ax, by - ay)
    v2 = (px - ax, py - ay)

    dot00 = v0[0]*v0[0] + v0[1]*v0[1]
    dot01 = v0[0]*v1[0] + v0[1]*v1[1]
    dot02 = v0[0]*v2[0] + v0[1]*v2[1]
    dot11 = v1[0]*v1[0] + v1[1]*v1[1]
    dot12 = v1[0]*v2[0] + v1[1]*v2[1]

    invDenom = 1 / (dot00 * dot11 - dot01 * dot01) if (dot00 * dot11 - dot01 * dot01) != 0 else 0
    u = (dot11 * dot02 - dot01 * dot12) * invDenom
    v = (dot00 * dot12 - dot01 * dot02) * invDenom
    return (u >= 0) and (v >= 0) and (u + v <= 1)

def project_to_line(p, a, b):
    # Projects point p onto line segment ab
    (px, py), (ax, ay), (bx, by) = p, a, b
    ab = (bx - ax, by - ay)
    ab2 = ab[0]**2 + ab[1]**2
    if ab2 == 0:
        return a
    t = ((px - ax) * ab[0] + (py - ay) * ab[1]) / ab2
    t = max(0, min(1, t))
    return (ax + t * ab[0], ay + t * ab[1])

def closest_point_in_triangle(p, a, b, c):
    # Project p onto each edge and return the one closest to p
    p_ab = project_to_line(p, a, b)
    p_bc = project_to_line(p, b, c)
    p_ca = project_to_line(p, c, a)
    d_ab = math.hypot(p[0]-p_ab[0], p[1]-p_ab[1])
    d_bc = math.hypot(p[0]-p_bc[0], p[1]-p_bc[1])
    d_ca = math.hypot(p[0]-p_ca[0], p[1]-p_ca[1])
    distances = [(d_ab, p_ab), (d_bc, p_bc), (d_ca, p_ca)]
    return min(distances, key=lambda x: x[0])[1]

async def set_color_direct(client, cmd_bytes):
    """
    Set color using direct byte commands
    """
    await client.write_gatt_char(COLOR_UUID, cmd_bytes, response=False)

async def main(addr):
    async with BleakClient(addr) as client:
        if client.is_connected:
            print("Connected to bulb")
            await client.write_gatt_char(POWER_UUID, b"\x01", response=False)   
            print("Bulb on")
            await asyncio.sleep(1)

            await client.write_gatt_char(BRIGHTNESS_UUID, b"\xfe", response=False)
            print("Brightness set to 100%")
            await asyncio.sleep(2)

            await set_color_hsv(0, 1.0, client)
            print("Blue") # blue
            await asyncio.sleep(2)

            print("Setting green")
            await set_color_direct(client, bytes([254, 0, 0, 254]))  # Green
            await asyncio.sleep(2)

            await set_color_hsv(300, 1.0, client)
            # await set_color_rgb(255, 255, 51, client) # 255, 255, 51 should be a yellow color, this output still blue
            print("Set yellow")
            await asyncio.sleep(5)

            print("Setting cyan")
            await set_color_direct(client, bytes([254, 0, 0, 100]))  # Cyan
            await asyncio.sleep(2)

            # Experimental - trying yellow
            print("Trying yellow 1")
            # Let's try mixing red and green parameters
            await set_color_direct(client, bytes([254, 254, 254, 150]))
            await asyncio.sleep(2)
            
            print("Trying yellow 2")
            # Try another combination
            await set_color_direct(client, bytes([254, 180, 254, 50]))
            await asyncio.sleep(2)
            
            # Try orange too (between red and yellow)
            print("Trying orange")
            await set_color_direct(client, bytes([254, 220, 254, 30]))
            await asyncio.sleep(2)

            await set_color_rgb(0, 153, 0, client) # 0, 153, 0 should be a green color, still doesn't change anything
            print("Set green")
            await asyncio.sleep(5)

        else:
            print("Failed to connect")

asyncio.run(main(MAC))
# asyncio.run(turn_off(MAC))
# asyncio.run(control_bulb(MAC))
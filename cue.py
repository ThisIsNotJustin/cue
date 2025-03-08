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
from bleak import BleakClient

MAC = "C7:46:23:94:4A:14"
POWER_UUID = "932c32bd-0002-47a2-835a-a8d455b859dd"
BRIGHTNESS_UUID = "932c32bd-0003-47a2-835a-a8d455b859dd"
TEMP_UUID = "932c32bd-0004-47a2-835a-a8d455b859dd"
COLOR_UUID = "932c32bd-0005-47a2-835a-a8d455b859dd"

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

asyncio.run(turn_off(MAC))
# asyncio.run(control_bulb(MAC))
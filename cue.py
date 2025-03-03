## Device C7:46:23:94:4A:14 Hue color lamp 2
import asyncio
from bleak import BleakClient

MAC = "C7:46:23:94:4A:14"
LIGHT_UUID = "932c32bd-0002-47a2-835a-a8d455b859dd"
BRIGHTNESS_UUID = "932c32bd-0003-47a2-835a-a8d455b859dd"
TEMP_UUID = "932c32bd-0004-47a2-835a-a8d455b859dd"
NOCLUE_UUID = "932c32bd-0006-47a2-835a-a8d455b859dd"
NOCLUEPT2_UUID = "932c32bd-1005-47a2-835a-a8d455b859dd"
NOCLUEPT3_UUID = "932c32bd-0007-47a2-835a-a8d455b859dd"

async def control_bulb(addr):
    async with BleakClient(addr) as client:
        if client.is_connected:
            print("Connected to bulb")

            for service in client.services:
                print(f"Service: {service.uuid}")
                for char in service.characteristics:
                    print(f"  Characteristic: {char.uuid}, Properties: {char.properties}")
            
            await client.write_gatt_char(LIGHT_UUID, b"\x01", response=False)
            print("Bulb on")
            await asyncio.sleep(1)

            await client.write_gatt_char(BRIGHTNESS_UUID, b"\x64", response=False)
            print("Brightness set to 100%")
            await asyncio.sleep(2)

            # does nothing atm
            await client.write_gatt_char(NOCLUE_UUID, b"\xFF", response=False)
            print("Something")
            await asyncio.sleep(2)

            # does nothing atm
            await client.write_gatt_char(NOCLUEPT2_UUID, b"\xFF", response=False)
            print("Something pt 2")
            await asyncio.sleep(2)

            # does nothing atm
            await client.write_gatt_char(NOCLUEPT3_UUID, b"\xFF", response=False)
            print("Something pt 3")
            await asyncio.sleep(2)

            # does nothing atm
            await client.write_gatt_char(TEMP_UUID, b"\x7F", response=False)
            print("Temp hopefully")
            await asyncio.sleep(2)
            
            await client.write_gatt_char(BRIGHTNESS_UUID, b"\x33", response=False)
            print("Brightness set to 20%")
            await asyncio.sleep(2)
            
            await client.write_gatt_char(LIGHT_UUID, b"\x00", response=False)
            print("Bulb off")
            
        else:
            print("Failed to connect")

asyncio.run(control_bulb(MAC))
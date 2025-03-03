## Device DF:AA:55:9E:FE:4E Hue color lamp 1
## Device CE:D6:DA:5C:AE:66 Hue color lamp 2
import asyncio
from bleak import BleakClient

async def control_bulb():
    async with BleakClient("DF:AA:55:9E:FE:4E") as client:
        for service in client.services:
            print(f"Service: {service.uuid}")
            for char in service.characteristics:
                print(f"  Characteristic: {char.uuid}")

        await client.write_gatt_char("932c32bd-0002-47a2-835a-a8d455b859dd", b"\x00")

asyncio.run(control_bulb())
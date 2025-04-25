import asyncio
from mavsdk import System
import math


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def get_scan_size():
    try:
        width = int(input("Enter the width to scan (in meters): "))
        height = int(input("Enter the height to scan (in meters): "))
        return width, height
    except ValueError:
        print("Error: Invalid input. Please enter valid numeric values.")
        return get_scan_size()


async def drone_screening():
    drone = System()
    print("Connecting to drone!")
    await drone.connect(system_address="udp://:14540")
    print("Drone connected!")
    print("Arming...")
    await drone.action.arm()
    print("Armed")

    width, height = get_scan_size()

    print("Taking off...")
    await drone.action.takeoff()
    await asyncio.sleep(10)

    print("Starting area scan...")
    step_lat = 3 / 111320  # ~2m in degrees to be faster
    step_lon = 3 / 111320

    home = await anext(drone.telemetry.position())
    home_lat = home.latitude_deg
    home_lon = home.longitude_deg
    alt = home.absolute_altitude_m + 4

    battery = await anext(drone.telemetry.battery())
    remaining = battery.remaining_percent

    total_distance_flown = 0.0
    prev_lat, prev_lon = home_lat, home_lon

    for i in range(width):
        for j in range(height):
            lon_offset = j * step_lon if i % 2 == 0 else (height - 1 - j) * step_lon
            lat_offset = i * step_lat

            target_lat = home_lat + lat_offset
            target_lon = home_lon + lon_offset

            distance = haversine(prev_lat, prev_lon, target_lat, target_lon)
            total_distance_flown += distance
            remaining -= distance * 1  # 1% per 1m

            await drone.action.goto_location(target_lat, target_lon, alt, 0)
            print(f"Flying to point ({target_lat}, {target_lon}, {alt})")
            print("Dropping seed 🌱")
            await asyncio.sleep(3)

            distance_home = haversine(target_lat, target_lon, home_lat, home_lon)
            estimated_needed = distance_home * 1

            print(f"🔋 Battery: {remaining:.2f}% | Distance to home: {distance_home:.2f} m")

            if remaining < estimated_needed:
                print("🚨 Battery too low to return home.")
                await drone.action.return_to_launch()
                return

            prev_lat, prev_lon = target_lat, target_lon

    print("✅ Scan complete. Returning to home.")
    await drone.action.return_to_launch()


asyncio.run(drone_screening())

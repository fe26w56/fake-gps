import subprocess

import os
import platform

def find_adb_path():
    """
    Finds the adb executable in common locations.
    """
    if platform.system() == "Windows":
        # Common paths for adb on Windows
        possible_paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Android", "sdk", "platform-tools", "adb.exe"),
            os.path.join(os.environ.get("ProgramFiles", ""), "Android", "Android Studio", "platform-tools", "adb.exe"),
        ]
    else:
        # Common paths for adb on macOS/Linux
        possible_paths = [
            os.path.expanduser("~/Library/Android/sdk/platform-tools/adb"),
            "/usr/local/bin/adb",
            "/usr/bin/adb",
        ]

    for path in possible_paths:
        if os.path.exists(path):
            return path
    return "adb" # Fallback to just 'adb' if not found in common paths

def get_connected_devices():
    """
    Executes 'adb devices' and returns a list of connected device IDs.
    """
    adb_path = find_adb_path()
    try:
        result = subprocess.run([adb_path, 'devices'], capture_output=True, text=True, check=True)
        output = result.stdout.strip().split('\n')
        devices = []
        # The first line is "List of devices attached", so skip it.
        for line in output[1:]:
            if line.strip():
                devices.append(line.split('\t')[0])
        return devices
    except FileNotFoundError:
        print(f"Error: '{adb_path}' command not found. Make sure Android SDK Platform-Tools are installed and in your PATH.")
        return []
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'adb devices': {e.stderr}")
        return []

def set_location(device_id, lat, lon, alt=0):
    """
    Sets the location of a given device.
    """
    adb_path = find_adb_path()
    try:
        # Enable mock locations
        subprocess.run([adb_path, '-s', device_id, 'shell', 'appops', 'set', 'com.google.android.apps.maps', 'android:mock_location', 'allow'], check=True)
        # Set the location
        subprocess.run([adb_path, '-s', device_id, 'shell', 'cmd', 'location', 'set', '--provider', 'gps', str(lat), str(lon), str(alt)], check=True)
        print(f"Location set to ({lat}, {lon}) on device {device_id}")
        return True
    except FileNotFoundError:
        print(f"Error: '{adb_path}' command not found.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error setting location on {device_id}: {e.stderr}")
        return False

from location_interpolator import LocationInterpolator
from logger import CsvLogger
import time

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Android Location Spoofer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 'set' command
    parser_set = subparsers.add_parser("set", help="Set a static location.")
    parser_set.add_argument("latitude", type=float, help="Latitude")
    parser_set.add_argument("longitude", type=float, help="Longitude")
    parser_set.add_argument("--altitude", type=float, default=0, help="Altitude (optional)")
    parser_set.add_argument("--device", help="Target device ID. If not specified, the first connected device will be used.")

    # 'move' command
    parser_move = subparsers.add_parser("move", help="Simulate movement between two points.")
    parser_move.add_argument("start_lat", type=float, help="Starting latitude")
    parser_move.add_argument("start_lon", type=float, help="Starting longitude")
    parser_move.add_argument("end_lat", type=float, help="Ending latitude")
    parser_move.add_argument("end_lon", type=float, help="Ending longitude")
    parser_move.add_argument("--speed", type=float, default=10.0, help="Speed in meters per second (default: 10 m/s)")
    parser_move.add_argument("--device", help="Target device ID. If not specified, the first connected device will be used.")

    # 'save_original' command
    parser_save = subparsers.add_parser("save", help="Save the current location to a file.")
    parser_save.add_argument("latitude", type=float, help="Current latitude to save")
    parser_save.add_argument("longitude", type=float, help="Current longitude to save")
    parser_save.add_argument("--device", help="Target device ID. If not specified, the first connected device will be used.")

    # 'restore' command
    parser_restore = subparsers.add_parser("restore", help="Restore the location from a file.")
    parser_restore.add_argument("--device", help="Target device ID. If not specified, the first connected device will be used.")


    args = parser.parse_args()

    devices = get_connected_devices()
    if not devices:
        print("No Android devices found.")
        exit(1)

    target_device = args.device if args.device else devices[0]
    if target_device not in devices:
        print(f"Error: Device '{target_device}' not found.")
        exit(1)

import json

def get_location_filename(device_id):
    # Sanitize device_id for use in a filename
    sanitized_id = device_id.replace(":", "_").replace("/", "_")
    return f".original_location_{sanitized_id}.json"

# ... (rest of the file)

if __name__ == '__main__':
    # ... (argument parser setup)

    # ... (device selection logic)

    if args.command == "set":
        set_location(target_device, args.latitude, args.longitude, args.altitude)

    elif args.command == "move":
        logger = CsvLogger(target_device)
        interpolator = LocationInterpolator(args.start_lat, args.start_lon, args.end_lat, args.end_lon, args.speed)
        print(f"Simulating movement on {target_device} for {interpolator.total_distance_meters:.2f} meters over {interpolator.total_time_seconds:.2f} seconds...")
        try:
            points_generator = interpolator.generate_points()
            logger.log(target_device, args.start_lat, args.start_lon)
            for i, (lat, lon) in enumerate(points_generator):
                print(f"Step {i+1}/{interpolator.steps}: Setting location to ({lat:.6f}, {lon:.6f})")
                if not set_location(target_device, lat, lon):
                    print("Aborting simulation.")
                    break
                logger.log(target_device, lat, lon)
                time.sleep(1)
            print("Simulation complete.")
        finally:
            logger.close()

    elif args.command == "save":
        location_data = {"latitude": args.latitude, "longitude": args.longitude}
        filename = get_location_filename(target_device)
        with open(filename, 'w') as f:
            json.dump(location_data, f)
        print(f"Location ({args.latitude}, {args.longitude}) saved for device {target_device} in {filename}")

    elif args.command == "restore":
        filename = get_location_filename(target_device)
        try:
            with open(filename, 'r') as f:
                location_data = json.load(f)
            print(f"Restoring location from {filename} for device {target_device}...")
            set_location(target_device, location_data['latitude'], location_data['longitude'])
        except FileNotFoundError:
            print(f"Error: No saved location file found for device {target_device}. Use the 'save' command first.")
        except (json.JSONDecodeError, KeyError):
            print(f"Error: The saved location file {filename} is corrupted.")

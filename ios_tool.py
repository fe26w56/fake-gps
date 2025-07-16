import subprocess
import json

def get_available_simulators():
    """
    Executes 'xcrun simctl list' and returns a dictionary of available simulators.
    """
    try:
        result = subprocess.run(['xcrun', 'simctl', 'list', '--json', 'devices'], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return data.get('devices', {})
    except FileNotFoundError:
        print("Error: 'xcrun' command not found. Make sure Xcode Command Line Tools are installed.")
        return {}
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'xcrun simctl list': {e.stderr}")
        return {}
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON output from 'xcrun simctl list'.")
        return {}

def set_location(device_udid, lat, lon):
    """
    Sets the location of a given device.
    """
    try:
        # For physical devices, you might need to use a different command or a library like libimobiledevice.
        # This example focuses on simulators.
        subprocess.run(['xcrun', 'simctl', 'location', device_udid, 'set', f'{lat},{lon}'], check=True)
        print(f"Location set to ({lat}, {lon}) on device {device_udid}")
        return True
    except FileNotFoundError:
        print("Error: 'xcrun' command not found.")
        return False
    except subprocess.CalledProcessError as e:
        # A common error is that the simulator is not booted.
        print(f"Error setting location on {device_udid}: {e.stderr}")
        print("Please ensure the simulator is booted and running.")
        return False

from location_interpolator import LocationInterpolator
from logger import CsvLogger
import time

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="iOS Location Spoofer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 'set' command
    parser_set = subparsers.add_parser("set", help="Set a static location.")
    parser_set.add_argument("udid", help="The UDID of the target simulator.")
    parser_set.add_argument("latitude", type=float, help="Latitude")
    parser_set.add_argument("longitude", type=float, help="Longitude")

    # 'move' command
    parser_move = subparsers.add_parser("move", help="Simulate movement between two points.")
    parser_move.add_argument("udid", help="The UDID of the target simulator.")
    parser_move.add_argument("start_lat", type=float, help="Starting latitude")
    parser_move.add_argument("start_lon", type=float, help="Starting longitude")
    parser_move.add_argument("end_lat", type=float, help="Ending latitude")
    parser_move.add_argument("end_lon", type=float, help="Ending longitude")
    parser_move.add_argument("--speed", type=float, default=10.0, help="Speed in meters per second (default: 10 m/s)")

    # 'save' command
    parser_save = subparsers.add_parser("save", help="Save the current location to a file.")
    parser_save.add_argument("udid", help="The UDID of the target simulator.")
    parser_save.add_argument("latitude", type=float, help="Current latitude to save")
    parser_save.add_argument("longitude", type=float, help="Current longitude to save")

    # 'restore' command
    parser_restore = subparsers.add_parser("restore", help="Restore the location from a file.")
    parser_restore.add_argument("udid", help="The UDID of the target simulator.")

    args = parser.parse_args()

import json

def get_location_filename(device_id):
    # Sanitize UDID for use in a filename
    sanitized_id = device_id.replace(":", "-").replace("(", "").replace(")", "").replace(" ", "")
    return f".original_location_{sanitized_id}.json"


if __name__ == '__main__':
    # ... (argument parser setup is above)
    args = parser.parse_args()

    if args.command == "set":
        set_location(args.udid, args.latitude, args.longitude)

    elif args.command == "move":
        logger = CsvLogger(args.udid.replace(':', '-')) # Sanitize UDID for filename
        interpolator = LocationInterpolator(args.start_lat, args.start_lon, args.end_lat, args.end_lon, args.speed)
        print(f"Simulating movement on {args.udid} for {interpolator.total_distance_meters:.2f} meters over {interpolator.total_time_seconds:.2f} seconds...")
        try:
            points_generator = interpolator.generate_points()
            logger.log(args.udid, args.start_lat, args.start_lon)
            for i, (lat, lon) in enumerate(points_generator):
                print(f"Step {i+1}/{interpolator.steps}: Setting location to ({lat:.6f}, {lon:.6f})")
                if not set_location(args.udid, lat, lon):
                    print("Aborting simulation.")
                    break
                logger.log(args.udid, lat, lon)
                time.sleep(1)
            print("Simulation complete.")
        finally:
            logger.close()

    elif args.command == "save":
        location_data = {"latitude": args.latitude, "longitude": args.longitude}
        filename = get_location_filename(args.udid)
        with open(filename, 'w') as f:
            json.dump(location_data, f)
        print(f"Location ({args.latitude}, {args.longitude}) saved for device {args.udid} in {filename}")

    elif args.command == "restore":
        filename = get_location_filename(args.udid)
        try:
            with open(filename, 'r') as f:
                location_data = json.load(f)
            print(f"Restoring location from {filename} for device {args.udid}...")
            set_location(args.udid, location_data['latitude'], location_data['longitude'])
        except FileNotFoundError:
            print(f"Error: No saved location file found for device {args.udid}. Use the 'save' command first.")
        except (json.JSONDecodeError, KeyError):
            print(f"Error: The saved location file {filename} is corrupted.")

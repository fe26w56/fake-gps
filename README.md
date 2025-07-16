# CLI Location Spoofer

This project provides a set of Python scripts to spoof the location of Android and iOS devices, both for setting a static location and simulating movement.

## Features

- **Static Location:** Set the GPS location of a device to specific latitude and longitude.
- **Movement Simulation:** Simulate movement from a start point to an end point at a given speed.
- **Platform Support:** Works for both Android (via `adb`) and iOS (simulators via `xcrun`).
- **Logging:** All movements are logged to a CSV file for auditing.
- **Revert:** Save and restore the original location of a device.

## Prerequisites

### General
- Python 3.12+
- `haversine` library (`pip install haversine`)

### For Android
- Android SDK Platform-Tools installed and `adb` in your system's PATH.
- An Android device with Developer Mode and USB Debugging enabled.

### For iOS
- macOS with Xcode and Xcode Command Line Tools installed.
- An iOS simulator (or a physical device with Developer Mode enabled on Xcode 17+).

## How to Use

The tool is split into two main scripts: `android_tool.py` and `ios_tool.py`.

### Common Commands

Both tools share a similar command structure:

- `set`: Sets a static location.
- `move`: Simulates movement between two points.
- `save`: Saves the current location coordinates to a file.
- `restore`: Restores the location from the saved file.

### Android Examples

**1. List connected devices:**
```bash
python android_tool.py
```
*(Note: This functionality is implicitly used by other commands to select a device)*

**2. Set a static location (e.g., Tokyo Station):**
```bash
python android_tool.py set 35.681236 139.767125
```

**3. Simulate a move from Tokyo Station to Akihabara Station at 5 m/s:**
```bash
python android_tool.py move 35.681236 139.767125 35.69836 139.773098 --speed 5
```

**4. Save the current location before spoofing:**
```bash
# Let's say your current location is Shibuya Crossing
python android_tool.py save 35.65952 139.700475
```

**5. Restore the original location:**
```bash
python android_tool.py restore
```

### iOS Examples

**1. Set a static location on a simulator:**
```bash
# Replace <YOUR_SIMULATOR_UDID> with your actual simulator's UDID
python ios_tool.py set <YOUR_SIMULATOR_UDID> 34.052235 -118.243683
```

**2. Simulate a move on a simulator:**
```bash
python ios_tool.py move <YOUR_SIMULATOR_UDID> 34.052235 -118.243683 34.056235 -118.248683 --speed 3
```

**3. Save and restore location (works the same as Android, just provide the UDID):**
```bash
python ios_tool.py save <YOUR_SIMULATOR_UDID> 34.052235 -118.243683
python ios_tool.py restore <YOUR_SIMULATOR_UDID>
```

## Logging

Each time the `move` command is executed, a log file named `teleport_log_{timestamp}_{device_id}.csv` is created in the same directory. This file contains timestamps and coordinates for each step of the simulation.
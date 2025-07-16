import csv
import datetime

class CsvLogger:
    def __init__(self, device_id):
        """
        Initializes the logger for a specific device.
        Creates a new CSV file with a timestamp in its name.
        """
        now = datetime.datetime.now()
        self.filename = f"teleport_log_{now.strftime('%Y%m%d_%H%M%S')}_{device_id}.csv"
        self.file = open(self.filename, 'w', newline='')
        self.writer = csv.writer(self.file)
        # Write header
        self.writer.writerow(['timestamp', 'device_id', 'latitude', 'longitude'])
        print(f"Logging to {self.filename}")

    def log(self, device_id, lat, lon):
        """
        Writes a single log entry to the CSV file.
        """
        timestamp = datetime.datetime.now().isoformat()
        self.writer.writerow([timestamp, device_id, lat, lon])

    def close(self):
        """
        Closes the CSV file.
        """
        self.file.close()
        print(f"Log file {self.filename} closed.")

if __name__ == '__main__':
    # Example Usage
    import time
    logger = CsvLogger("test_device_01")
    logger.log("test_device_01", 35.681236, 139.767125)
    time.sleep(1)
    logger.log("test_device_01", 35.681323, 139.767155)
    time.sleep(1)
    logger.log("test_device_01", 35.681410, 139.767186)
    logger.close()

from haversine import haversine, Unit
import time

class LocationInterpolator:
    def __init__(self, start_lat, start_lon, end_lat, end_lon, speed_mps):
        """
        Initializes the interpolator with start/end points and speed.

        :param start_lat: Starting latitude
        :param start_lon: Starting longitude
        :param end_lat: Ending latitude
        :param end_lon: Ending longitude
        :param speed_mps: Speed in meters per second
        """
        self.start_point = (start_lat, start_lon)
        self.end_point = (end_lat, end_lon)
        self.speed_mps = speed_mps

        self.total_distance_meters = haversine(self.start_point, self.end_point, unit=Unit.METERS)
        if self.speed_mps <= 0:
            self.total_time_seconds = 0
        else:
            self.total_time_seconds = self.total_distance_meters / self.speed_mps

        self.steps = int(self.total_time_seconds) # 1-second intervals

    def calculate_intermediate_point(self, fraction):
        """
        Calculates an intermediate point on a great-circle path.
        Formula from: http://www.movable-type.co.uk/scripts/latlong.html
        """
        lat1, lon1 = self.start_point
        lat2, lon2 = self.end_point

        # Not doing a full great-circle path calculation for simplicity,
        # a simple linear interpolation is sufficient for short distances.
        intermediate_lat = lat1 + (lat2 - lat1) * fraction
        intermediate_lon = lon1 + (lon2 - lon1) * fraction
        return intermediate_lat, intermediate_lon

    def generate_points(self):
        """
        Generator that yields a new coordinate point for each step of the journey.
        """
        if self.steps <= 0:
            # If the journey is instant, just yield the end point
            yield self.end_point
            return

        for i in range(1, self.steps + 1):
            fraction = i / self.steps
            yield self.calculate_intermediate_point(fraction)

if __name__ == '__main__':
    # Example usage: Tokyo Station to Akihabara Station (approx 1.7km)
    start_lat, start_lon = 35.681236, 139.767125 # Tokyo Station
    end_lat, end_lon = 35.69836, 139.773098     # Akihabara Station

    # Walking speed: 1.4 m/s
    # Car speed: 10 m/s
    speed = 10 # m/s

    interpolator = LocationInterpolator(start_lat, start_lon, end_lat, end_lon, speed)

    print(f"Total distance: {interpolator.total_distance_meters:.2f} meters")
    print(f"Estimated time: {interpolator.total_time_seconds:.2f} seconds")
    print(f"Number of steps (1-sec intervals): {interpolator.steps}")
    print("-" * 30)

    points_generator = interpolator.generate_points()

    for i, point in enumerate(points_generator):
        print(f"Step {i+1}/{interpolator.steps}: Lat={point[0]:.6f}, Lon={point[1]:.6f}")
        time.sleep(1)

    print("-" * 30)
    print("Destination reached.")

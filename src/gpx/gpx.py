from math import radians, sin, cos, asin, sqrt

class GPX:

    EARTH_RADIUS = 6371008.8

    def __init__(self, point_list = None):
        if point_list is None:
            point_list = []
        self.point_list = point_list
        self.set_point_distances()
        self.total_distance = None
        self.get_total_distance()
        self.total_time = None
        self.moving_time = None
        self.set_moving_total_time()

    def format_time(self, time_seconds: int):
        seconds = time_seconds % 60
        hours, minutes = divmod(time_seconds // 60, 60)
        formatted_seconds = f"{seconds:>02}\""
        formatted_minutes = f"{minutes:>02}'"
        formatted_hours = f"{hours}h"
        if hours > 0:
            return f"{formatted_hours}{formatted_minutes}{formatted_seconds}"
        if minutes > 0:
            return f"{formatted_minutes}{formatted_seconds}"
        return formatted_seconds

    def format_distance(self, distance: int):
        if distance > 300:
            return f"{(distance // 10) / 100}km"
        return f"{distance}m"

    def format_pace(self, pace: float):
        minutes = int(pace)
        seconds = int((pace - minutes) * 60 + 0.5)
        return f"{minutes}'{seconds:>02}\"/km"

    def total_stats(self):
        return  (f"Total time: {self.format_time(int(self.total_time))}\n"
                f"Moving time: {self.format_time(int(self.moving_time))}\n"
                f"Distance: {self.format_distance(int(self.total_distance))}")

    def haversine(self, lat1, lon1, lat2, lon2):
        p1, p2 = radians(lat1), radians(lat2)
        dp = p2 - p1
        dl = radians(lon2 - lon1)
        a = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
        return 2 * GPX.EARTH_RADIUS * asin(sqrt(a))

    def set_point_distances(self) -> None:
        total_distance = 0
        for index in range(len(self.point_list) - 1):
            prev_lat = self.point_list[index]["lat"]
            prev_lon = self.point_list[index]["lon"]
            new_lat = self.point_list[index + 1]["lat"]
            new_lon = self.point_list[index + 1]["lon"]
            seconds_diff = (self.point_list[index + 1]["time"] - self.point_list[index]["time"]).total_seconds()
            if seconds_diff <= 5.1:
                self.point_list[index]["distance"] = self.haversine(prev_lat, prev_lon, new_lat, new_lon)
                total_distance += self.point_list[index]["distance"]
            self.point_list[index]["total_distance"] = total_distance

    def get_total_distance(self) -> float:
        if self.total_distance is not None:
            return self.total_distance
        self.total_distance = 0
        for index in range(len(self.point_list) - 1, -1, -1):
            if self.point_list[index].get("total_distance") is not None:
                self.total_distance = self.point_list[index]["total_distance"]
                break
        return self.total_distance

    def set_moving_total_time(self) -> None:
        total_time = 0
        moving_time = 0
        for index in range(len(self.point_list)):
            delta_time = (self.point_list[index]["time"] - self.point_list[(index - 1) if index > 0 else 0]["time"]).total_seconds()
            total_time += delta_time
            if delta_time <= 5.1:
                moving_time += delta_time

            self.point_list[index]["total_time"] = int(total_time)
            self.point_list[index]["moving_time"] = int(moving_time)

        self.total_time = int(total_time)
        self.moving_time = int(moving_time)
        print(self.total_time, self.moving_time)

    def get_index_at(self, time: int) -> int:
        start = 0
        end = len(self.point_list)
        while start < end:
            middle = start + (end - start) // 2
            if self.point_list[middle]["moving_time"] <= time < self.point_list[middle + 1]["moving_time"]:
                return middle
            elif time > self.point_list[middle]["moving_time"]:
                start = middle + 1
            else:
                end = middle
        return start

    def get_float_index_at(self, time: float) -> float:
        start = 0
        end = len(self.point_list)
        while start < end:
            middle = start + (end - start) // 2
            if self.point_list[middle]["moving_time"] <= time < self.point_list[middle + 1]["moving_time"]:
                return start + (time - self.point_list[middle]["moving_time"]) / (self.point_list[middle + 1]["moving_time"] - self.point_list[middle]["moving_time"])
            elif time > self.point_list[middle]["moving_time"]:
                start = middle + 1
            else:
                end = middle
        return start
     
    def get_pace_at(self, time: int) -> float:
        segment_duration = 20
        start = self.get_index_at(time - segment_duration)
        end = self.get_index_at(time)
        distance_intermediate = self.point_list[end]["total_distance"] - self.point_list[start]["total_distance"]
        pace = (segment_duration / 60) / (distance_intermediate / 1000)
        return pace

    def get_distance_at(self, time: int) -> int:
        return int(self.point_list[self.get_index_at(time)]["total_distance"])

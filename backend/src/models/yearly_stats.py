class YearlyStats:
    def __init__(
        self,
        athlete_id: int,
        year: int,
        total_distance: float,
        total_moving_time: float,
        total_elevation_gain: float,
    ):
        self.athlete_id = athlete_id
        self.year = year
        self.total_distance = total_distance
        self.total_moving_time = total_moving_time
        self.total_elevation_gain = total_elevation_gain

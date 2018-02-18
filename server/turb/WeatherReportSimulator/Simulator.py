from .Flight_Statistics.Statistics_Fun import airport_statistics, airport_info
from datetime import datetime, timedelta
from .Weather_Data.Weather_Fun import *
from random import randint, uniform
from netCDF4 import Dataset
from . import definitions
import numpy as np
import matplotlib.pyplot as plt
from geopy.distance import vincenty
import time
import pickle
from collections import deque
import copy

FLIGHT_HEIGHT = 6000

class Aircraft:
    def __init__(self, type: str, weight: float):
        self.type = type
        self.weight = weight

    def __str__(self):
        return '(' + str(self.type) + ', ' + str(self.weight) + ')'


class WeatherReport:
    """Represents a weather report sent by a plane.

    Attributes:
        time (datetime): Time the weather report was received at.
        lat (float): Latitude the weather report was sent at.
        lon (float): Longitude the weather report was sent at.
        level (float):
        tke (float): Ambient turbulent kinetic energy in J/kg.
    """

    def __init__(self, time: datetime, aircraft: Aircraft, lat: float, lon: float, wind_x: float, wind_y: float,
                 altitude: float, tke: float):
        """
        :param time: Time the weather report was received at.
        :param lat: Longitude the weather report was created at.
        :param lon: Longitude the weather report was created at.
        :param level:
        :param tke: Ambient turbulent kinetic energy in J/kg.
        """
        self.time = time
        self.aircraft = aircraft
        self.lat = lat
        self.lon = lon
        self.altitude = altitude
        self.wind_x = wind_x
        self.wind_y = wind_y
        self.tke = tke

    def __str__(self):
        return ', '.join([self.time.strftime('%H:%M.%S'), str(self.aircraft), str(self.lat), str(self.lon),
                          str(self.altitude), str(self.wind_x), str(self.wind_y), str(self.tke)])


class Flight:
    """Represents a flight.

    Attributes:
        start (str): Starting location of the flight.
        end (str): Ending location of the flight.
        start_time (datetime): Time the flight took off.
        end_time (datetime): Time the flight landed.
        plane_type (str): Plane type.
    """

    def __init__(self, start: str, end: str, start_time: datetime, end_time: datetime, plane: Aircraft):
        """Creates a new flight with the given parameters.

        :param plane: Plane type.
        :param start: Starting location of the flight.
        :param end: Ending location of the flight.
        :param start_time: Time the flight took off.
        :param end_time: Time the flight landed.

        """
        self.start = start
        self.end = end
        self.start_time = start_time
        self.end_time = end_time
        self.plane = plane

    def __str__(self):
        return ', '.join([str(self.start), str(self.end), self.start_time.strftime('%H:%M.%S'), str(self.plane)])


class FlightsGenerator:
    """Generates flights randomly starting at a given time with a given frequency.

        Attributes:
            current_time (datetime): Current time of the generator.
            average_time (float): Average expected time between flights in seconds.
    """

    def __init__(self, start_time: datetime, average_time: timedelta):
        """
        Creates a new FlightsGenerator.

        :param start_time: Time that the generator will begin at.
        :param average_time: Frequency that flights should be generated at in Hz.
        """
        self.start_time = start_time
        self.current_time = start_time
        self.average_time = average_time
        self._airports, self._origin_probabilities, self._conditional_probabilities = airport_statistics()
        self._plane_probabilities = {Aircraft('Cessna 172', 100): .2, Aircraft('Boeing 747', 100): .5,
                                     Aircraft('Airbus A380', 100): .3}
        self._airport_info = airport_info()

    def next_flight(self) -> Flight:
        """Generates and returns a new flight randomly, progresses the current time of the generator.

        :return: The next generated flight.
        """
        flight_speed = 245  # m / s
        dt = np.random.gamma(self.average_time.seconds)
        self.current_time = self.current_time + timedelta(seconds=dt)
        origin = weighted_random(self._origin_probabilities)
        dest = weighted_random(self._conditional_probabilities[origin])
        plane_type = weighted_random(self._plane_probabilities)
        start_lat, start_lon, _ = self._airport_info[origin]
        end_lat, end_lon, _ = self._airport_info[dest]
        flight_time = vincenty((start_lat, start_lon), (end_lat, end_lon)).meters / flight_speed
        return Flight(origin, dest, self.current_time, self.current_time + timedelta(seconds=flight_time), plane_type)


class FlightsSimulator:

    def __init__(self, flight_generator: FlightsGenerator):
        """Creates a new flights simulator.

        :param flight_generator: Flight generator.
        :param stabilize_time: How far in advance of start_time the simulator should begin in seconds.
        """
        self.current_time = copy.deepcopy(flight_generator.current_time)
        self.active_flights = []
        self._flight_generator = flight_generator
        self.average_time = flight_generator.average_time
        self._leftover_flight = None
        self._airport_info = airport_info()

    def progress(self, d_time: timedelta) -> None:
        """Moves the simulation forward for the given time.

        :param d_time: How far ahead to progress the simulation in seconds.
        """
        stop_time = self.current_time + d_time

        if self._leftover_flight is not None and self._leftover_flight.start_time <= stop_time:
            self.active_flights.append(self._leftover_flight)
            self._leftover_flight = None

        new_active_flights = []

        while self._flight_generator.current_time < stop_time:
            new_flight = self._flight_generator.next_flight()
            if new_flight.start_time <= stop_time:
                if new_flight.end_time > stop_time:
                    new_active_flights.append(new_flight)
            else:
                self._leftover_flight = new_flight

        for flight in self.active_flights:
            if flight.end_time > stop_time:
                new_active_flights.append(flight)

        self.active_flights = new_active_flights
        self.current_time = stop_time

    def get_location(self, flight):
        if flight not in self.active_flights:
            return None
        else:
            info_start = self._airport_info[flight.start]
            if info_start is None:
                return None
            lat_start, lon_start, alt_start = info_start

            info_end = self._airport_info[flight.end]
            if info_end is None:
                return None
            lat_end, lon_end, alt_end = info_end

            percent_complete = (self.current_time - flight.start_time) / (flight.end_time - flight.start_time)

            lat_start_shift = lat_start + 90
            lat_end_shift = lat_end + 90
            cur_lat_shift = 0
            dif_a = (lat_end_shift - lat_start_shift) % 180
            dif_b = (lat_start_shift - lat_end_shift) % 180
            if dif_a < dif_b:
                cur_lat_shift = (percent_complete * dif_a + lat_start_shift) % 180
            else:
                cur_lat_shift = (-percent_complete * dif_b + lat_start_shift) % 180
            cur_lat = cur_lat_shift - 90

            lon_start_shift = lon_start + 180
            lon_end_shift = lon_end + 180
            cur_lon_shift = 0
            dif_a = (lon_end_shift - lon_start_shift) % 360
            dif_b = (lon_start_shift - lon_end_shift) % 360
            if dif_a < dif_b:
                cur_lon_shift = (percent_complete * dif_a + lon_start_shift) % 360
            else:
                cur_lon_shift = (-percent_complete * dif_b + lon_start_shift) % 360
            cur_lon = cur_lon_shift - 180

            return cur_lat, cur_lon


class WeatherReportGenerator:
    """Simulates generation of weather reports using a given flight simulator, weather model,
    and report frequency.

        Attributes:
            current_time (datetime): Current time of the simulation.
    """

    def __init__(self, flight_sim: FlightsSimulator, weather_model: WeatherModel, average_report_time: timedelta):
        """Creates a new WeatherReportGenerator.

        :param flight_sim: Flight simulator.
        :param weather_model: Weather model.
        :param average_report_time: Average expected time between reports in seconds.
        """
        self._flight_sim = flight_sim
        self._average_report_time = average_report_time
        self.current_time = copy.deepcopy(flight_sim.current_time)
        self._weather = weather_model
        self._airport_info = airport_info()

    def next_report(self):
        """Generates and returns a new weather report randomly, progresses the current time of the generator.

        :return: The next generated weather report.
        """
        dt = np.random.gamma(self._average_report_time.seconds)
        self.current_time = self.current_time + timedelta(seconds=dt)
        self._flight_sim.progress(timedelta(seconds=dt))
        flight = self._flight_sim.active_flights[randint(0, len(self._flight_sim.active_flights) - 1)]
        cur_lat, cur_lon = self._flight_sim.get_location(flight)
        tke, uwnd, vwnd = self._weather.get_weather(cur_lat, cur_lon, FLIGHT_HEIGHT, self.current_time)
        if tke is None or uwnd is None or vwnd is None:
            return None
        return WeatherReport(self.current_time, flight.plane, cur_lat, cur_lon, uwnd, vwnd, FLIGHT_HEIGHT, tke)


class WeatherReportSimulator:
    def __init__(self, report_generator: WeatherReportGenerator, keep_time: timedelta):
        self._report_generator = report_generator
        self.keep_time = keep_time
        self.current_reports = deque()
        self.current_time = copy.deepcopy(report_generator.current_time)
        self._leftover_report = None

    def progress(self, d_time: timedelta) -> None:
        stop_time = self.current_time + d_time

        if self._leftover_report is not None and self._leftover_report.time <= stop_time:
            self.current_reports.append(self._leftover_report)
            self._leftover_report = None

        while self._report_generator.current_time < stop_time:
            new_report = self._report_generator.next_report()
            if new_report is not None:
                if new_report.time <= stop_time:
                    self.current_reports.append(new_report)
                else:
                    self._leftover_report = new_report

        while len(self.current_reports) > 0 and self.current_reports[0].time < stop_time - self.keep_time:
            self.current_reports.popleft()

        self.current_time = stop_time

    @classmethod
    def get_default(cls):
        tke = Dataset(definitions.TKE_DIR, 'r')
        uwnd = Dataset(definitions.UWND_DIR, 'r')
        vwnd = Dataset(definitions.VWND_DIR, 'r')
        hgt = Dataset(definitions.HGT_DIR, 'r')
        start_time = datetime(year=1800, month=1, day=1, hour=0, minute=0, second=0) \
                     + timedelta(hours=tke['time'][0]) - timedelta(hours=3)
        reg1 = pickle.load(open(definitions.INDEX_1_REGRESSION_DIR, 'rb'))
        reg2 = pickle.load(open(definitions.INDEX_2_REGRESSION_DIR, 'rb'))
        index_predictor = IndexPredictor(tke['lat'], tke['lon'], reg1, reg2)
        weather_model = WeatherModel(tke, uwnd, vwnd, hgt, index_predictor)
        flight_generator = FlightsGenerator(start_time, timedelta(seconds=20))
        flight_simulator = FlightsSimulator(flight_generator)
        flight_simulator.progress(timedelta(hours=3))
        report_generator = WeatherReportGenerator(flight_simulator, weather_model, timedelta(seconds=10))
        return WeatherReportSimulator(report_generator, timedelta(hours=1))


def weighted_random(distribution: dict):
    """Randomly selects an element according to the given distribution. Probabilities do not need to be normalized.

    :param distribution: Dictionary from possible objects to probability of selection.
    :return: An elements of the given dictionary that is selected with the corresponding probability.
    """
    if np.any([distribution[x] < 0 for x in distribution]):
        raise ValueError('All probability values must be non-negative.')
    r = uniform(0, np.sum([distribution[x] for x in distribution]))
    tot = 0
    i = 0
    for x in distribution:
        i += 1
        tot += distribution[x]
        if tot >= r:
            return x
        if i == len(distribution):
            return x


"""
tke = Dataset(definitions.TKE_DIR, 'r')
uwnd = Dataset(definitions.UWND_DIR, 'r')
vwnd = Dataset(definitions.VWND_DIR, 'r')
hgt = Dataset(definitions.HGT_DIR, 'r')
start_time = datetime(year=1800, month=1, day=1, hour=0, minute=0, second=0)\
             + timedelta(hours=tke['time'][0]) - timedelta(hours=3)

reg1 = pickle.load(open(definitions.INDEX_1_REGRESSION_DIR, 'rb'))
reg2 = pickle.load(open(definitions.INDEX_2_REGRESSION_DIR, 'rb'))
index_predictor = IndexPredictor(tke['lat'], tke['lon'], reg1, reg2)
weather_model = WeatherModel(tke, uwnd, vwnd, hgt, index_predictor)
flight_generator = FlightsGenerator(start_time, timedelta(seconds=20))
flight_simulator = FlightsSimulator(flight_generator)
flight_simulator.progress(timedelta(hours=3))
report_generator = WeatherReportGenerator(flight_simulator, weather_model, timedelta(seconds=10))
report_simulator = WeatherReportSimulator(report_generator, timedelta(hours=1))
start = time.time()
report_simulator.progress(timedelta(hours=2))
for report in report_simulator.current_reports:
    print(report)
print(len(report_simulator.current_reports))

plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111)

while True:
    ax.clear()
    locations = [flight_simulator.get_location(f) for f in flight_simulator.active_flights]
    print(len(locations))
    ax.scatter([l[1] for l in locations], [l[0] for l in locations], s=0.5)
    ax.scatter([-84.38, -80.2, -118.25, -122.32, -157.82, -145.9, -74], [33.75, 25.77, 34.05, 47.6, 21.3, 61.2, 40.8], s=2, c='r')
    plt.xlim(-170, -60)
    plt.ylim(10, 70)
    fig.canvas.draw()
    flight_simulator.progress(60)
"""

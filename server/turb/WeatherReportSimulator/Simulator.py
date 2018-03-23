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
    """Represents an aircraft type."""

    def __init__(self, name: str, weight: float):
        """Creates a new aircraft.

        :param name: Aircraft name
        :param weight: Aircraft weight in Kg
        """
        self.name = name
        self.weight = weight
        self.db_id = None


class Airport:
    """Represents an airport."""

    def __init__(self, code: str, name: str, lat: float, lon: float, alt: float):
        """Creates a new airport

        :param code: Airport's IATA code
        :param name: Airport name
        :param lat: Latitude
        :param lon: Longitude
        :param alt: Altitude in meters
        """
        self.code = code
        self.name = name
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.db_id = None


class Flight:
    """Represents a flight."""

    uid = 0

    def __init__(self, origin: Airport, dest: Airport, start_time: datetime,
                 end_time: datetime, plane: Aircraft, lat: float, lon: float,
                 alt: float):
        """Creates a new flight.

        :param plane: Plane type.
        :param origin: Starting location of the flight.
        :param dest: Ending location of the flight.
        :param start_time: Time the flight took off.
        :param end_time: Time the flight landed.
        :param lat: Current flight Latitude
        :param lon: Current flight Longitude
        :param alt: Current flight altitude in meters
        """
        self.origin = origin
        self.dest = dest
        self.start_time = start_time
        self.end_time = end_time
        self.plane = plane
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.identifier = str(Flight.uid)
        Flight.uid += 1
        self.db_id = None


class WeatherReport:
    """Represents a weather report sent by a plane."""

    def __init__(self, time: datetime, flight: Flight, lat: float, lon: float,
                alt: float, wind_x: float, wind_y: float, tke: float):
        """
        :param time: Time the weather report was received at.
        :param flight: Flight that created this weather report
        :param lat: Longitude the weather report was created at.
        :param lon: Longitude the weather report was created at.
        :param alt: Altitude the weather report was created at.
        :param wind_x: Absolute zonal wind speed in m/s.
        :param wind_y: Absolute meridional wind speed in m/s.
        :param tke: Ambient turbulent kinetic energy in J/kg.
        """
        self.time = time
        self.flight = flight
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.wind_x = wind_x
        self.wind_y = wind_y
        self.tke = tke
        self.db_id = None


class FlightsGenerator:
    """Generates flights randomly starting at a given time with a given  expected frequency."""

    def __init__(self, start_time: datetime, average_time: timedelta):
        """
        Creates a new flight generator.

        :param start_time: Time that the generator will begin at.
        :param average_time: Expected time between flights in seconds.
        """
        self._current_time = start_time
        self._average_time = average_time
        self._airports, self._origin_probabilities, self._conditional_probabilities = airport_statistics()
        self._plane_probabilities = {Aircraft('Cessna 172', 100): .2, Aircraft('Boeing 747', 100): .5,
                                     Aircraft('Airbus A380', 100): .3}
        self._airport_info = airport_info()

    def next_flight(self) -> Flight:
        """Generates and returns a new flight randomly, and progresses the current time of the generator.

        :return: The next generated flight.
        """
        flight_speed = 245  # m / s
        dt = np.random.gamma(self.average_time.seconds)
        self.current_time = self.current_time + timedelta(seconds=dt)
        origin = weighted_random(self._origin_probabilities)
        dest = weighted_random(self._conditional_probabilities[origin])
        plane_type = weighted_random(self._plane_probabilities)
        start_lat, start_lon, start_alt = self._airport_info[origin]
        end_lat, end_lon, end_alt = self._airport_info[dest]
        flight_time = vincenty((start_lat, start_lon), (end_lat, end_lon)).meters / flight_speed
        return Flight(Airport(origin, origin, start_lat, start_lon, start_alt),
                      Airport(dest, dest, end_lat, end_lon, end_alt),
                      self.current_time,
                     self.current_time + timedelta(seconds=flight_time),
                     plane_type, 0, 0, FLIGHT_HEIGHT)

    @property
    def flight_time(self):
        return self._average_time

    @property
    def current_time(self):
        return self._current_time

class FlightsSimulator:
    """Stores active flights created by a flight generator, and keeps track of active flights."""

    def __init__(self, flight_generator: FlightsGenerator):
        """Creates a new flight simulator.

        :param flight_generator: Flight generator.
        :param stabilize_time: How far in advance of start_time the simulator should begin in seconds.
        """
        self._current_time = copy.deepcopy(flight_generator.current_time)
        self._active_flights = []
        self._flight_generator = flight_generator
        self._leftover_flight = None
        self._airport_info = airport_info()

    def progress(self, d_time: timedelta):
        """Moves the simulation forward for the given time.

        :param d_time: How far ahead to progress the simulation in seconds.
        """
        stop_time = self.current_time + d_time

        if self._leftover_flight is not None and self._leftover_flight.start_time <= stop_time:
            self._active_flights.append(self._leftover_flight)
            self._leftover_flight = None

        new_active_flights = []

        while self._flight_generator.current_time < stop_time:
            new_flight = self._flight_generator.next_flight()
            if new_flight.start_time <= stop_time:
                if new_flight.end_time > stop_time:
                    new_active_flights.append(new_flight)
            else:
                self._leftover_flight = new_flight

        for flight in self._active_flights:
            if flight.end_time > stop_time:
                new_active_flights.append(flight)

        self._active_flights = new_active_flights
        for flight in self._active_flights:
            flight.lat, flight.lon = self.get_location(flight)
        self._current_time = stop_time

    def get_location(self, flight):
        """Returns the latitude and longitude of an active flight.

        :param flight: Flight to find the position of
        :return: Tuple containing the latitude and longitude of the given flight if it is active, otherwise None
        """
        if flight not in self.active_flights:
            return None
        else:
            lat_start = flight.origin.lat
            lon_start = flight.origin.lon
            alt_start = flight.origin.alt

            lat_end = flight.dest.lat
            lon_end = flight.dest.lon
            alt_end = flight.dest.alt

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
            flight.lat = cur_lat
            flight.lon = cur_lon
            return cur_lat, cur_lon

    def current_flights(self):
        """Gets the currently active flights.

        :return: List of the current active flights.
        """
        return self._active_flights

    @property
    def flight_time(self):
        return self._flight_generator.flight_time

    @property
    def current_time(self):
        return self._current_time


class WeatherReportGenerator:
    """Simulates generation of weather reports using a given flight simulator, weather model, and report frequency."""

    def __init__(self, flight_sim: FlightsSimulator, weather_model: WeatherModel, average_report_time: timedelta):
        """Creates a new WeatherReportGenerator.

        :param flight_sim: Flight simulator.
        :param weather_model: Weather model.
        :param average_report_time: Average expected time between reports in seconds.
        """
        self._flight_sim = flight_sim
        self._average_report_time = average_report_time
        self._current_time = copy.deepcopy(flight_sim.current_time)
        self._weather = weather_model
        self._airport_info = airport_info()

    def next_report(self):
        """Generates and returns a new weather report randomly, and progresses the current time of the generator.

        :return: The next generated weather report.
        """
        dt = np.random.gamma(self._average_report_time.seconds)
        self._current_time = self.current_time + timedelta(seconds=dt)
        self._flight_sim.progress(timedelta(seconds=dt))
        flight = self._flight_sim.active_flights[randint(0, len(self._flight_sim.active_flights) - 1)]
        cur_lat, cur_lon = self._flight_sim.get_location(flight)
        weather = self._weather.get_weather(cur_lat, cur_lon, FLIGHT_HEIGHT, self.current_time)
        if weather is None:
            return None
        tke, uwnd, vwnd = weather
        return WeatherReport(self.current_time, flight, cur_lat, cur_lon,
                             FLIGHT_HEIGHT, uwnd, vwnd, tke)

    def current_flights(self):
        """Gets the currently active flights.

        :return: List of the current active flights.
        """
        return self._flight_sim.current_flights()

    @property
    def flight_time(self):
        return self._flight_sim.flight_time


    @property
    def report_time(self):
        return self._average_report_time

    @property
    def current_time(self):
        return self._current_time

class WeatherReportSimulator:
    """Simulates storage of active weather reports."""

    def __init__(self, report_generator: WeatherReportGenerator, keep_time: timedelta):
        self._report_generator = report_generator
        self._keep_time = keep_time
        self._current_reports = deque()
        self._new_reports = []
        self.removed_reports = []
        self._current_time = copy.deepcopy(report_generator.current_time)
        self._leftover_report = None

    def progress(self, d_time: timedelta):
        stop_time = self._current_time + d_time
        self._new_reports = []
        self.removed_reports = []

        if self._leftover_report is not None and self._leftover_report.time <= stop_time:
            self._current_time.append(self._leftover_report)
            self._new_reports.append(self._leftover_report)
            self._leftover_report = None

        while self._report_generator.current_time < stop_time:
            new_report = self._current_time.next_report()
            if new_report is not None:
                if new_report.time <= stop_time:
                    self._current_reports.append(new_report)
                    self._new_reports.append(new_report)
                else:
                    self._leftover_report = new_report

        while len(self._current_reports) > 0 and self._current_reports[0].time < stop_time - self._keep_time:
            removed = self._current_reports.popleft()
            self.removed_reports.append(removed)

        self._current_time = stop_time

    @property
    def flight_time(self):
        return self._flight_sim.flight_time

    @property
    def report_time(self):
        return self._average_report_time

    @property
    def keep_time(self):
        return self._keep_time

    @property
    def current_time(self):
        return self._current_time

    def current_flights(self):
        """Gets the currently active flights.

        :return: List of the current active flights.
        """
        return self._report_generator.current_flights()

    @classmethod
    def get_simulator(cls, flight_time: float=20, report_time: float=10, parallel: bool=False):
        data = Dataset(definitions.WEATHER_DATA_DIR, 'r', parallel=parallel)
        start_time = datetime(year=1800, month=1, day=1, hour=0, minute=0, second=0) \
                     + timedelta(hours=data['time'][0]) - timedelta(hours=3)
        try:
            reg1, reg2 = pickle.load(open(definitions.INDEX_REGRESSION_DIR, 'rb'))
            index_predictor = IndexPredictor(data['lat'], data['lon'], reg1, reg2)
        except:
            index_predictor = IndexPredictor(data['lat'], data['lon'])
            pickle.dump(index_predictor.get_predictors(), open(definitions.INDEX_REGRESSION_DIR, 'wb'))
        weather_model = WeatherModel(data, data, data, data, index_predictor)
        flight_generator = FlightsGenerator(start_time, timedelta(seconds=flight_time))
        flight_simulator = FlightsSimulator(flight_generator)
        flight_simulator.progress(timedelta(hours=3))
        report_generator = WeatherReportGenerator(flight_simulator, weather_model, timedelta(seconds=report_time))
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

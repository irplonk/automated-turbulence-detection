from datetime import datetime, timedelta
from random import randint, uniform
from netCDF4 import Dataset
import time
import pickle
import copy
import math
from . import definitions
from .Flight_Statistics.Statistics_Fun import airport_statistics, airport_info
from .Weather_Data.Weather_Fun import *


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
                 alt: float, bearing: float):
        """Creates a new flight.

        :param plane: Plane type.
        :param origin: Starting location of the flight.
        :param dest: Ending location of the flight.
        :param start_time: Time the flight took off.
        :param end_time: Time the flight landed.
        :param lat: Current flight Latitude
        :param lon: Current flight Longitude
        :param alt: Current flight altitude in meters
        :param bearing: Current flight bearing in degrees
        """
        self.origin = origin
        self.dest = dest
        self.start_time = start_time
        self.end_time = end_time
        self.plane = plane
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.bearing = bearing
        self.identifier = str(Flight.uid)
        Flight.uid += 1
        self.db_id = None


class WeatherReport:
    """Represents a weather report sent by a plane."""

    def __init__(self, time: datetime, flight: Flight, lat: float, lon: float,
                 alt: float, wind_x: float, wind_y: float, tke: float):
        """
        :param time: Date and time the weather report was received at.
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


def get_angular_distance(lat1, lon1, lat2, lon2):
    """
    Returns the angular great circle distance from the first
    coordinate to the second coordinate
    """
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * \
        math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return c


def get_distance(lat1, lon1, lat2, lon2, alt):
    """
    Returns the great circle distance in meters from the first
    coordinate to the second coordinate at the given altitude
    """
    r = 6371000 + alt  # radius from center of Earth in meters
    return r * get_angular_distance(lat1, lon1, lat2, lon2)


def get_inter_point(lat1, lon1, lat2, lon2, x):
    """
    Returns the intermediate point between the two given points
    on the great circle that is x proportion from the first to the second
    """
    d = get_angular_distance(lat1, lon1, lat2, lon2)
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    a = math.sin((1 - x) * d) / math.sin(d)
    b = math.sin(x * d) / math.sin(d)
    x = a * math.cos(lat1) * math.cos(lon1) + b * \
        math.cos(lat2) * math.cos(lon2)
    y = a * math.cos(lat1) * math.sin(lon1) + b * \
        math.cos(lat2) * math.sin(lon2)
    z = a * math.sin(lat1) + b * math.sin(lat2)
    lati = math.atan2(z, math.sqrt(x**2 + y**2))
    loni = math.atan2(y, x)
    return math.degrees(lati), math.degrees(loni)


def get_bearing(lat1, lon1, lat2, lon2):
    """
    Returns the great circle bearing in degrees from the first
    coordinate to the second coordinate
    """
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    y = math.sin(lon2 - lon1) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * \
        math.cos(lat2) * math.cos(lon2 - lon1)
    return math.degrees(math.atan2(y, x))


class FlightGenerator:
    """Generates flights randomly starting at a given time with a given  expected frequency."""

    def __init__(self, average_time: timedelta):
        """
        Creates a new flight generator.

        :param average_time: Expected time between flights in seconds.
        """
        self._average_time = average_time
        self._airports, self._origin_probabilities, self._conditional_probabilities = airport_statistics()
        self._plane_probabilities = {Aircraft('Cessna 172', 100): .2, Aircraft('Boeing 747', 100): .5,
                                     Aircraft('Airbus A380', 100): .3}
        self._airport_info = airport_info()

    def next_flight(self, current_time: datetime):
        """Generates and returns a new flight randomly

        :return: The next generated flight
        """
        flight_speed = 245  # m / s
        dt = np.random.gamma(self._average_time.seconds)
        flight_start = current_time + timedelta(seconds=dt)
        origin = weighted_random(self._origin_probabilities)
        dest = weighted_random(self._conditional_probabilities[origin])
        plane_type = weighted_random(self._plane_probabilities)
        start_lat, start_lon, start_alt = self._airport_info[origin]
        end_lat, end_lon, end_alt = self._airport_info[dest]
        flight_time = get_distance(
            start_lat, start_lon, end_lat, end_lon, FLIGHT_HEIGHT) / flight_speed
        bearing = get_bearing(start_lat, start_lon, end_lat, end_lon)
        return Flight(Airport(origin, origin, start_lat, start_lon, start_alt),
                      Airport(dest, dest, end_lat, end_lon, end_alt),
                      flight_start,
                      flight_start + timedelta(seconds=flight_time),
                      plane_type, 0, 0, FLIGHT_HEIGHT, bearing)

    @property
    def flight_time(self):
        return self._average_time


class FlightSimulator:
    """Stores active flights created by a flight generator, and keeps track of active flights."""

    def __init__(self, current_time: datetime, flight_generator: FlightGenerator):
        """Creates a new flight simulator.

        :param current_time: Starting time
        :param flight_generator: Flight generator.
        """
        self._current_time = current_time
        self._active_flights = []
        self._new_flights = []
        self._removed_flights = []
        self._flight_generator = flight_generator
        self._leftover_flight = None
        self._airport_info = airport_info()

    def progress(self, d_time: timedelta):
        """Moves the simulation forward for the given time.

        :param d_time: How far ahead to progress the simulation in seconds.
        """
        stop_time = self.current_time + d_time
        self._new_flights = []
        self._removed_flights = []

        if self._leftover_flight is not None and self._leftover_flight.start_time <= stop_time:
            self._new_flights.append(self._leftover_flight)
            self._leftover_flight = None

        progressed_time = self._current_time

        while progressed_time < stop_time:
            new_flight = self._flight_generator.next_flight(progressed_time)
            if new_flight is None:
                break
            progressed_time = new_flight.start_time
            if new_flight.start_time <= stop_time:
                if new_flight.end_time > stop_time:
                    self._new_flights.append(new_flight)
            else:
                self._leftover_flight = new_flight

        all_flights = []

        for flight in self._new_flights + self._active_flights:
            if flight.end_time > stop_time:
                all_flights.append(flight)
                self.get_location(flight)
            else:
                self._removed_flights.append(flight)

        self._active_flights = all_flights
        self._current_time = stop_time

    def get_location(self, flight):
        """Updates and returns the latitude, longitude, and bearing of an active flight.

        :param flight: Flight to find the position of
        :return: Tuple containing the latitude, longitude and bearing of the
                 given flight if it is active, otherwise None
        """
        if flight not in self._active_flights:
            return None
        else:
            lat_start = flight.origin.lat
            lon_start = flight.origin.lon
            alt_start = flight.origin.alt

            lat_end = flight.dest.lat
            lon_end = flight.dest.lon
            alt_end = flight.dest.alt

            percent_complete = (
                self.current_time - flight.start_time) / (flight.end_time - flight.start_time)

            cur_lat, cur_lon = get_inter_point(
                lat_start, lon_start, lat_end, lon_end, percent_complete)
            cur_bearing = get_bearing(cur_lat, cur_lon, lat_end, lon_end)

            flight.lat = cur_lat
            flight.lon = cur_lon
            flight.bearing = cur_bearing

            return cur_lat, cur_lon, cur_bearing

    @property
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

    def __init__(self, weather_model: WeatherModel, average_report_time: timedelta):
        """Creates a new WeatherReportGenerator.

        :param weather_model: Weather model.
        :param average_report_time: Average expected time between reports in seconds.
        """
        self._average_report_time = average_report_time
        self._weather = weather_model
        self._airport_info = airport_info()

    def next_report(self, current_time: datetime, flights):
        """Generates and returns a new weather report randomly, and progresses the current time of the generator.

        :param current_time: Current time.
        :param flights: Current active flights.
        :return: The next generated weather report.
        """
        dt = np.random.gamma(self._average_report_time.seconds)
        if len(flights) == 0:
            return None
        flight = flights[randint(0, len(flights) - 1)]
        cur_lat, cur_lon, cur_alt = flight.lat, flight.lon, flight.alt
        report_time = current_time + timedelta(seconds=dt)
        weather = self._weather.get_weather(
            cur_lat, cur_lon, cur_alt, report_time)
        if weather is None:
            return None
        tke, uwnd, vwnd = weather
        return WeatherReport(report_time, flight, cur_lat, cur_lon, cur_alt,
                             uwnd, vwnd, tke)

    @property
    def report_time(self):
        return self._average_report_time


class WeatherReportSimulator:
    """Simulates storage of active weather reports."""

    def __init__(self, flight_simulator: FlightSimulator,
                 report_generator: WeatherReportGenerator,
                 keep_time: timedelta):
        self._flight_simulator = flight_simulator
        self._report_generator = report_generator
        self._keep_time = keep_time
        self._current_reports = []
        self._new_reports = []
        self._removed_reports = []
        self._current_time = copy.deepcopy(flight_simulator.current_time)
        self._leftover_report = None

    def progress(self, d_time: timedelta):
        self._flight_simulator.progress(d_time)
        stop_time = self._current_time + d_time
        self._new_reports = []
        self._removed_reports = []

        if self._leftover_report is not None and self._leftover_report.time <= stop_time:
            self._new_reports.append(self._leftover_report)
            self._leftover_report = None

        progressed_time = self._current_time
        while progressed_time < stop_time:
            new_report = self._report_generator.next_report(progressed_time,
                                                            self._flight_simulator.current_flights)
            if new_report is None:
                break
            progressed_time = new_report.time
            if new_report is not None:
                if new_report.time <= stop_time:
                    self._new_reports.append(new_report)
                else:
                    self._leftover_report = new_report

        all_reports = []
        for r in self._new_reports + self._current_reports:
            if r.time < stop_time - self._keep_time:
                self._removed_reports.append(r)
            else:
                all_reports.append(r)

        self._current_reports = all_reports
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

    @property
    def current_flights(self):
        """Gets the currently active flights.

        :return: List of the current active flights
        """
        return self._flight_simulator.current_flights

    @property
    def removed_flights(self):
        """Gets the flights which have completed in the last iteration.

        :return: List of the current completed flights.
        """
        return self._flight_simulator._removed_flights

    @property
    def new_reports(self):
        """Gets a list of new reports on this iteration.

        :return: List of the reports generated on this progression
        """
        return self._new_reports

    @property
    def removed_reports(self):
        """Gets a list of removed reports on this iteration.

        :return: List of the reports removed on this progression
        """
        return self._removed_reports

    @classmethod
    def get_simulator(cls, flight_time: float=20, report_time: float=10, parallel: bool=False):
        data = Dataset(definitions.WEATHER_DATA_DIR, 'r', parallel=parallel)
        start_time = datetime(year=1800, month=1, day=1, hour=0, minute=0, second=0) \
            + timedelta(hours=data['time'][0])
        try:
            reg1, reg2 = pickle.load(
                open(definitions.INDEX_REGRESSION_DIR, 'rb'))
            index_predictor = IndexPredictor(
                data['lat'], data['lon'], reg1, reg2)
        except:
            index_predictor = IndexPredictor(data['lat'], data['lon'])
            pickle.dump(index_predictor.get_predictors(), open(
                definitions.INDEX_REGRESSION_DIR, 'wb'))
        weather_model = WeatherModel(data, data, data, data, index_predictor)
        flight_generator = FlightGenerator(timedelta(seconds=flight_time))
        flight_simulator = FlightSimulator(start_time, flight_generator)
        # flight_simulator.progress(timedelta(hours=3))
        report_generator = WeatherReportGenerator(
            weather_model, timedelta(seconds=report_time))
        simulator = WeatherReportSimulator(
            flight_simulator, report_generator, timedelta(hours=1))
        # simulator.progress(timedelta(hours=1))
        return simulator


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

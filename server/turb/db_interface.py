from .models import *
from datetime import datetime, timedelta
from .WeatherReportSimulator import Simulator
import pytz

def add_aircraft(aircraft: Simulator.Aircraft) -> Aircraft:
    in_db = Aircraft.objects.filter(aircraft_type=aircraft.name,
                                    weight=aircraft.weight)
    if in_db.exists():
        return in_db[0]
    else:
        model = Aircraft(aircraft_type=aircraft.name, weight=aircraft.weight)
        model.save()
        return model

def add_airport(airport: Simulator.Airport) -> Airport:
    in_db = Airport.objects.filter(airport_code=airport.code)
    if in_db.exists():
        return in_db[0]
    else:
        model = Airport(airport_code=airport.code, airport_name=airport.name,
                        latitude=airport.lat, longitude=airport.lon,
                        altitude=airport.alt)
        model.save()
        return model

def add_flight(flight: Simulator.Flight) -> Flight:
    origin = add_airport(flight.origin)
    dest = add_airport(flight.dest)
    aircraft = add_aircraft(flight.plane)
    in_db = Flight.objects.filter(origin=origin, destination=dest,
                                  identifier=flight.identifier)
    if in_db.exists():
        model = in_db[0]
        model.latitude = flight.lat
        model.longitude = flight.lon
        model.altitude = flight.alt
        model.save()
        return model
    else:
        model = Flight(start_time=flight.start_time.replace(tzinfo=pytz.UTC),
                       origin=origin, destination=dest, latitude=flight.lat,
                       longitude=flight.lon, altitude=flight.alt,
                       aircraft=aircraft, identifier=flight.identifier)
        model.save()
        return model

def add_report(report: Simulator.WeatherReport) -> WeatherReport:
    flight = add_flight(report.flight)
    report = WeatherReport(time=report.time.replace(tzinfo=pytz.UTC),
                           flight=flight, latitude=report.lat,
                           longitude=report.lon, altitude=report.alt,
                           wind_x=report.wind_x, wind_y=report.wind_y,
                           tke=report.tke)
    report.save()
    return report

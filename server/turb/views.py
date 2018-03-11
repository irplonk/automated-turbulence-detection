from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.generic import TemplateView
from django import forms
from django.core import serializers
from django.utils import timezone
from django.forms.models import model_to_dict
from .models import *
from datetime import datetime, timedelta
import random
from .WeatherReportSimulator import Simulator
from multiprocessing.dummy import Process
import threading
import time
from datetime import timedelta
import pytz

class SimulationForm(forms.Form):
    flight_time = forms.FloatField(label='flight_time')
    report_time = forms.FloatField(label='report_time')
    update_time = forms.FloatField(label='update_time')
    time_per_update = forms.FloatField(label='time_per_update')

class SimulationView(TemplateView):
    sim_state = 'stopped'
    model_aircrafts = {}
    simulation_thread = None

    def get(self, request: HttpRequest) -> HttpResponse:
        form = SimulationForm()
        return render(request, 'simulation.html', {'sim_state':SimulationView.sim_state, 'form': form})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = SimulationForm(request.POST)
        if 'start_stop' in request.POST:
            if SimulationView.sim_state in ['running', 'paused']:
                SimulationView.simulation_thread.unpause()
                if SimulationView.simulation_thread is not None:
                    SimulationView.simulation_thread.stop()
                SimulationView.simulation_thread = None
                SimulationView.sim_state = 'stopped'
            elif SimulationView.sim_state == 'stopped':
                if form.is_valid():
                    flight_time = form.cleaned_data['flight_time']
                    report_time = form.cleaned_data['report_time']
                    update_time = form.cleaned_data['update_time']
                    time_per_update = form.cleaned_data['time_per_update']
                    t = SimulationThread(flight_time, report_time, update_time, time_per_update)
                    t.start()
                    SimulationView.simulation_thread = t
                    SimulationView.sim_state = 'running'
        elif 'pause' in request.POST:
            if SimulationView.sim_state == 'running':
                SimulationView.sim_state = 'paused'
                SimulationView.simulation_thread.pause()
            elif SimulationView.sim_state == 'paused':
                SimulationView.simulation_thread.unpause()
                SimulationView.sim_state = 'running'
        return render(request, 'simulation.html', {
            'cur_flight_time': 10,
            'cur_report_time': 20,
            'update_time': 1,
            'time_per_update': 100,
            'sim_state':SimulationView.sim_state})

class SimulationThread(threading.Thread):
    def __init__(self, flight_time, report_time, update_time, time_per_update):
        super(SimulationThread, self).__init__()
        self.flight_time = flight_time
        self.report_time = report_time
        self.update_time = update_time
        self.time_per_update = time_per_update
        self.sim = Simulator.WeatherReportSimulator.get_simulator(flight_time, report_time)
        self._stop_event = threading.Event()
        self._unpause_event = threading.Event()
        self._unpause_event.set()

    def run(self):
        keep_time = timedelta(hours=2)
        WeatherReport.objects.all().delete()
        Flight.objects.all().delete()
        Aircraft.objects.all().delete()
        Airport.objects.all().delete()
        model_aircrafts = {}
        while not self.stopped():
            self._unpause_event.wait()
            start = time.time()
            self.sim.progress(timedelta(seconds=self.time_per_update))
            for report in self.sim.new_reports:
                add_report(report)
            n = 0
            for report in WeatherReport.objects.filter(time__lte=(self.sim.current_time - keep_time).replace(tzinfo=pytz.UTC)).all():
                n += 1
                report.delete()
            print(str(len(self.sim.new_reports)) + ' new reports')
            print(str(n) + ' removed reports')
            dif = time.time() - start
            if dif < self.update_time:
                time.sleep(self.update_time - dif)
            else:
                print('simulation progressing ' + str(dif - self.update_time) + 's too slow')

    def stop(self):
        print('simulation stopped')
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def pause(self):
        print('simulation paused')
        self._unpause_event.clear()

    def unpause(self):
        print('simulation unpaused')
        self._unpause_event.set()

    def paused(self):
        return self._pause_event.is_set()

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

def display(request: HttpRequest) -> HttpResponse:
    max_entries = safe_cast(request.GET.get('max', -1), int, -1)
    start_index = safe_cast(request.GET.get('start', 0), int, 0)
    table_name = request.GET.get('table', '')

    if table_name == 'aircraft':
        entries = Aircraft.objects.all()
        db_attrs = ['aircraft_type', 'weight']
    elif table_name == 'airports':
        entries = Airport.objects.all()
        db_attrs = ['airport_code', 'latitude', 'longitude', 'altitude']
    elif table_name == 'flights':
        entries = Flight.objects.all()
        db_attrs = ['identifier', 'start_time', 'latitude', 'longitude', 'altitude']
    elif table_name == 'reports':
        entries = WeatherReport.objects.all()
        db_attrs = ['time', 'latitude', 'longitude', 'altitude',
                    'wind_x', 'wind_y', 'tke']
    else:
        return HttpResponse('Invalid table name {}'.format(table_name))
    if max_entries < 0:
        entries = [[getattr(e, attr) for attr in db_attrs] for e in entries[start_index:]]
    else:
        entries = [[getattr(e, attr) for attr in db_attrs] for e in entries[start_index:start_index + max_entries]]

    return render(request, 'display_db.html',
        {'entries': entries,
        'db_attrs': db_attrs,
        'table': table_name,
        'max_entries': max_entries,
        'start_index': start_index,
        'end_index': start_index + len(entries) - 1})

def query(request: HttpRequest) -> HttpResponse:
    max_entries = safe_cast(request.GET.get('max', -1), int, -1)
    start_index = safe_cast(request.GET.get('start', 0), int, 0)
    table_name = request.GET.get('table', '')

    if table_name == 'airplanes':
        entries = Aircraft.objects.all()
    elif table_name == 'airports':
        entries = Airport.objects.all()
    elif table_name == 'reports':
        entries = WeatherReport.objects.all()
    else:
        return JsonResponse({"entries": []})

    if max_entries < 0:
        return JsonResponse({"entries": [model_to_dict(r) for r in entries[start_index:]]})
    else:
        return JsonResponse({"entries": [model_to_dict(r) for r in entries[start_index:start_index + max_entries]]})

def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html', {})

def safe_cast(val, typ, default):
    try:
        return typ(val)
    except ValueError:
        return default

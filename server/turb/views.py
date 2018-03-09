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
        keep_time = timedelta(hours=1)
        WeatherReport.objects.all().delete()
        Aircraft.objects.all().delete()
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

def add_report(report: Simulator.WeatherReport):
    if Aircraft.objects.filter(aircraft_type=report.aircraft.type,
        weight=report.aircraft.weight).exists():
        model_aircraft = Aircraft.objects.filter(aircraft_type=report.aircraft.type,
            weight=report.aircraft.weight)[0]
    else:
        model_aircraft = Aircraft(aircraft_type=report.aircraft.type,
            weight=report.aircraft.weight)
        model_aircraft.save()
    WeatherReport(
        time=report.time.replace(tzinfo=pytz.UTC),
        latitude=report.lat,
        longitude=report.lon,
        altitude=report.altitude,
        aircraft_type=model_aircraft,
        wind_x=report.wind_x,
        wind_y=report.wind_y,
        tke=report.tke).save()

def display(request: HttpRequest) -> HttpResponse:
    max_entries = safe_cast(request.GET.get('max', -1), int, -1)
    start_index = safe_cast(request.GET.get('start', 0), int, 0)
    table_name = request.GET.get('table', '')

    if table_name == 'airplanes':
        entries = Aircraft.objects.all()
        db_attrs = ['aircraft_type', 'weight']
    elif table_name == 'airports':
        entries = Airport.objects.all()
        db_attrs = ['airport_code', 'airport_name']
    elif table_name == 'reports':
        entries = WeatherReport.objects.all()
        db_attrs = ['time', 'latitude', 'longitude', 'altitude', 'aircraft_type',
                    'wind_x', 'wind_y', 'tke']
    else:
        return HttpResponse('Invalid table name {}'.format(table_name))
    if max_entries < 0:
        return render(request, 'display_db.html.html',
            {'entries': [[getattr(e, attr) for attr in db_attrs] for e in entries[start_index:]],
            'db_attrs': db_attrs})
    else:
        return render(request, 'display_db.html',
            {'entries': [[getattr(e, attr) for attr in db_attrs] for e in entries[start_index:start_index + max_entries]],
            'db_attrs': db_attrs})

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

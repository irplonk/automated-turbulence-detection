from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.views.generic import TemplateView
from django import forms
from .models import *
from datetime import datetime, timedelta
import random
from .WeatherReportSimulator import Simulator
from multiprocessing.dummy import Process
import threading
import time
from datetime import timedelta


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
            if SimulationView.sim_state == 'running':
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
            'time_per_update': 300,
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
        WeatherReport.objects.all().delete()

        model_aircrafts = {}

        while not self.stopped():
            for report in self.sim.new_reports:
                if report.aircraft in model_aircrafts:
                    model_aircraft = model_aircrafts[report.aircraft]
                else:
                    model_aircraft = Aircraft(aircraft_type=report.aircraft.type,
                        weight=report.aircraft.weight)
                    model_aircrafts[report.aircraft] = model_aircraft
                    model_aircraft.save()
                WeatherReport(time=report.time,
                    latitude=report.lat,
                    longitude=report.lon,
                    altitude=report.altitude,
                    aircraft_type=model_aircraft,
                    wind_x=report.wind_x,
                    wind_y=report.wind_y,
                    tke=report.tke).save()
            for report in self.sim.removed_reports:
                if report.aircraft in model_aircrafts:
                    model_aircraft = model_aircrafts[report.aircraft]
                else:
                    model_aircraft = Aircraft(aircraft_type=report.aircraft.type,
                        weight=report.aircraft.weight)
                    model_aircrafts[report.aircraft] = model_aircraft
                    model_aircraft.save()
                for db_report in WeatherReport.objects.filter(time=report.time,
                    latitude=report.lat,
                    longitude=report.lon,
                    altitude=report.altitude,
                    aircraft_type=model_aircraft,
                    wind_x=report.wind_x,
                    wind_y=report.wind_y,
                    tke=report.tke).all():
                    db_report.delete()
            print(str(len(self.sim.new_reports)) + ' new reports')
            print(str(len(self.sim.removed_reports)) + ' removed reports')

            self._unpause_event.wait()
            start = time.time()
            self.sim.progress(timedelta(seconds=self.time_per_update))
            dif = time.time() - start
            if dif < self.update_time:
                time.sleep(self.update_time - dif)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def pause(self):
        self._unpause_event.clear()

    def unpause(self):
        self._unpause_event.set()

    def paused(self):
        return self._pause_event.is_set()

def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html', {})

def del_db(request: HttpRequest) -> HttpResponse:
    """
    for plane in Aircraft.objects.all()[:4]:
        plane.delete()
    """
    return HttpResponse('Database deleted')

def make_db(request: HttpRequest) -> HttpResponse:
    model_aircrafts = {}
    simulator = Simulator.WeatherReportSimulator.get_default()
    simulator.progress(timedelta(hours=2))
    print('Simulation completed')

    """
    for report in simulator.current_reports:
        if report.aircraft in model_aircrafts:
            model_aircraft = model_aircrafts[report.aircraft]
        else:
            model_aircraft = Aircraft(aircraft_type=report.aircraft.type,
                weight=report.aircraft.weight)
            model_aircrafts[report.aircraft] = model_aircraft
            model_aircraft.save()

        report = WeatherReport(time=report.time,
            latitude=report.lat,
            longitude=report.lon,
            altitude=report.altitude,
            aircraft_type=model_aircraft,
            wind_x=report.wind_x,
            wind_y=report.wind_y,
            tke=report.tke).save()
    """
    return HttpResponse('Database remade')

def airplanes(request: HttpRequest) -> HttpResponse:
    return render(request, 'airplanes.html',
        {'airplanes': Aircraft.objects.all()})

def airports(request: HttpRequest) -> HttpResponse:
    return render(request, 'airports.html',
        {'airports': Airport.objects.all()})

def reports(request: HttpRequest) -> HttpResponse:
    return reports_page(request, 1)

def reports_page(request: HttpRequest, page_num: int) -> HttpResponse:
    return render(request, 'reports.html',
        {'reports': WeatherReport.objects.all()[100*(page_num-1):100*page_num]})

from __future__ import unicode_literals
from django import forms
from django.forms.models import model_to_dict
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.generic import TemplateView
from django.core import serializers
from django.utils import timezone
from .models import *
from .WeatherReportSimulator import Simulator
from .WeatherReportSimulator.Multithreading import SimulationThreadManager
from .db_interface import *

class SimulationForm(forms.Form):
    flight_time = forms.FloatField(label='flight_time', initial=10)
    report_time = forms.FloatField(label='report_time', initial=20)
    update_time = forms.FloatField(label='update_time', initial=1)
    time_per_update = forms.FloatField(label='time_per_update', initial=100)

class SimulationView(TemplateView):
    sim_state = 'stopped'
    cur_flight_time = 10
    cur_report_time = 20
    cur_update_time = 1
    cur_time_per_update = 100
    model_aircrafts = {}
    simulation_thread = None

    def get(self, request: HttpRequest) -> HttpResponse:
        form = SimulationForm()
        return render(request, 'simulation.html',
            {
                'sim_state': SimulationView.sim_state,
                'cur_flight_time': SimulationView.cur_flight_time,
                'cur_report_time': SimulationView.cur_report_time,
                'cur_update_time': SimulationView.cur_update_time,
                'cur_time_per_update': SimulationView.cur_time_per_update
        })

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
                    SimulationView.cur_flight_time = flight_time
                    report_time = form.cleaned_data['report_time']
                    SimulationView.cur_report_time = report_time
                    update_time = form.cleaned_data['update_time']
                    SimulationView.cur_update_time = update_time
                    time_per_update = form.cleaned_data['time_per_update']
                    SimulationView.cur_time_per_update = time_per_update
                    t = SimulationThreadManager(flight_time, report_time, update_time, time_per_update, 1)
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
        return render(request, 'simulation.html',
            {
                'sim_state': SimulationView.sim_state,
                'cur_flight_time': SimulationView.cur_flight_time,
                'cur_report_time': SimulationView.cur_report_time,
                'cur_update_time': SimulationView.cur_update_time,
                'cur_time_per_update': SimulationView.cur_time_per_update
        })

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
        db_attrs = ['identifier', 'active', 'start_time', 'latitude', 'longitude', 'bearing', 'altitude']
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
    id = safe_cast(request.GET.get('id', -1), int, -1)
    table_name = request.GET.get('table', '')
    
    if table_name == 'airplanes':
        entries = Aircraft.objects
    elif table_name == 'airports':
        entries = Airport.objects
    elif table_name == 'reports':
        entries = WeatherReport.objects
    elif table_name == 'flights':
        entries = Flight.objects.filter(active=True)
    else:
        return JsonResponse({"entries": []})

    if id >= 0:
        entries = entries.filter(id=id)
    entries = entries.all()

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

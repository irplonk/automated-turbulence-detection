from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from .models import *
from datetime import datetime, timedelta
import random
from .WeatherReportSimulator import Simulator

def index(request: HttpRequest):
    return render(request, 'index.html', {})

def del_db(request: HttpRequest):
    """
    for plane in Aircraft.objects.all()[:4]:
        plane.delete()
    """
    return HttpResponse('Database deleted')

def make_db(request: HttpRequest):
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

def airplanes(request: HttpRequest):
    return render(request, 'airplanes.html',
        {'airplanes': Aircraft.objects.all()})

def airports(request: HttpRequest):
    return render(request, 'airports.html',
        {'airports': Airport.objects.all()})

def reports(request: HttpRequest):
    return reports_page(request, 1)

def reports_page(request: HttpRequest, page_num: int):
    return render(request, 'reports.html',
        {'reports': WeatherReport.objects.all()[100*(page_num-1):100*page_num]})

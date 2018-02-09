# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from models import Aircraft

# Create your views here.


def index(request):
    aircraft = Aircraft(1, 'C150', 100)
    aircraft.save()
    return HttpResponse('<h1>Hello, World!</h1>')

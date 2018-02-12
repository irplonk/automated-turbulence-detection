# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
from . import models
import os

PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(PACKAGE_ROOT, os.pardir, os.pardir)

# Create your views here.

def index(request):
    return HttpResponse(open(os.path.join(PROJECT_ROOT, 'Starter.html'), "r"))

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db import connection

# Create your models here.


class Aircraft(models.Model):
    aircraft_type = models.CharField(max_length=10, primary_key=True)
    weight = models.DecimalField(max_digits=20, decimal_places=2)


class WeatherReport(models.Model):
    time = models.DateTimeField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    altitude = models.DecimalField(max_digits=9, decimal_places=6)
    aircraft_type = models.ForeignKey(Aircraft, on_delete=models.CASCADE)
    wind_x = models.DecimalField(max_digits=5, decimal_places=2)
    wind_y = models.DecimalField(max_digits=5, decimal_places=2)
    tke = models.DecimalField(max_digits=5, decimal_places=2)


class Airport(models.Model):
    airport_code = models.CharField(max_length=3, primary_key=True)
    airport_name = models.TextField()

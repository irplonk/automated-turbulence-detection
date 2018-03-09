from __future__ import unicode_literals
from django.db import models
from django.db import connection


class Aircraft(models.Model):
    id = models.AutoField(primary_key=True)
    aircraft_type = models.CharField(max_length=10)
    weight = models.DecimalField(max_digits=20, decimal_places=2)


class WeatherReport(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    altitude = models.DecimalField(max_digits=9, decimal_places=1)
    aircraft_type = models.ForeignKey(Aircraft, on_delete=models.CASCADE)
    wind_x = models.DecimalField(max_digits=6, decimal_places=3)
    wind_y = models.DecimalField(max_digits=6, decimal_places=3)
    tke = models.DecimalField(max_digits=6, decimal_places=4)


class Airport(models.Model):
    id = models.AutoField(primary_key=True)
    airport_code = models.CharField(max_length=3)
    airport_name = models.TextField()

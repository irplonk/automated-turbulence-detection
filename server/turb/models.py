from __future__ import unicode_literals
from django.db import models
from django.db import connection


class Aircraft(models.Model):
    id = models.AutoField(primary_key=True)
    aircraft_type = models.TextField()
    weight = models.DecimalField(max_digits=6, decimal_places=0)


class Airport(models.Model):
    id = models.AutoField(primary_key=True)
    airport_code = models.CharField(max_length=3)
    airport_name = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    altitude = models.DecimalField(max_digits=9, decimal_places=1)


class Flight(models.Model):
    id = models.AutoField(primary_key=True)
    start_time = models.DateTimeField()
    origin = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="origin")
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="dest")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    altitude = models.DecimalField(max_digits=9, decimal_places=1)
    bearing = models.DecimalField(max_digits=9, decimal_places=6)
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE)
    active = models.BooleanField()
    identifier = models.TextField()


class WeatherReport(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    altitude = models.DecimalField(max_digits=9, decimal_places=1)
    wind_x = models.DecimalField(max_digits=9, decimal_places=6)
    wind_y = models.DecimalField(max_digits=9, decimal_places=6)
    tke = models.DecimalField(max_digits=6, decimal_places=4)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)

from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('simulation/', views.SimulationView.as_view(), name='simulation'),
    path('display', views.display, name='display'),
    path('query', views.query, name='query')
]

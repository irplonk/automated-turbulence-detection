from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('make_db/', views.make_db, name='make_db'),
    path('del_db/', views.del_db, name='del_db'),
    path('airplanes/', views.airplanes, name='airplanes'),
    path('airports/', views.airports, name='airports'),
    path('reports/', views.reports, name='reports'),
    path('reports/<int:page_num>/', views.reports_page, name='reports_page')
]

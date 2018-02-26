import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FLIGHTS_DIR = ROOT_DIR + '/Flight_Statistics/Flights.csv'
WEATHER_DATA_DIR = ROOT_DIR + '/Weather_Data/all.201708_week1.nc'
TKE_DIR = ROOT_DIR + '/Weather_Data/tke.201708.nc'
UWND_DIR = ROOT_DIR + '/Weather_Data/uwnd.201708.nc'
VWND_DIR = ROOT_DIR + '/Weather_Data/vwnd.201708.nc'
HGT_DIR = ROOT_DIR + '/Weather_Data/hgt.201708.nc'
AIRPORTS_DIR = ROOT_DIR + '/Flight_Statistics/Airport_Locations.csv'
INDEX_1_REGRESSION_DIR = ROOT_DIR + '/index_1_reg.pickle'
INDEX_2_REGRESSION_DIR = ROOT_DIR + '/index_2_reg.pickle'

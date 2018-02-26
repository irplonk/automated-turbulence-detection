# automated-turbulence-detection
Fall 2017-Spring 2018 Junior Design Project with Honeywell

### Set up
You must install `django-environ` to do this run the following line:
```
pip install django-environ
```
Then, create a file named `.env` in `server/server` which will look like this:
```
DEBUG=on
SECRET_KEY='your_secret_key'
DB_HOST='your_db_host'
DB_NAME='your_db_name'
DB_USER='your_db_user'
DB_PASSWORD='your_db_password'
DB_PORT=''
```

### Running
To run the application, run the following line in `server`:
```
python manage.py runserver
```
and navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
To use a local database instead, run
```
python local_manage.py runserver
```
If you make changes to any files while the server is running, it is not
necessary to restart it. All changes will be present once you reload the webpage.

### Simulation Control
In order to run the simulator, the `.nc` weather file must be placed
in `server/turb/WeatherReportSimulator/Weather_Data`.
To control the simulation, navigate to [http://127.0.0.1:8000/simulation/](http://127.0.0.1:8000/simulation/).
From here the simulation can be started, stopped, and paused.
The flight_time parameter controls how frequently in (simulated) seconds new flights will be generated.
The report_time parameter controls how frequently in (simulated) seconds new weather reports will be generated.
The update_time parameter controls how frequently in (real) seconds the simulation will insert new weather reports.
The time_per_update parameter controls how far the simulation will progress in (simulated) seconds each iteration.

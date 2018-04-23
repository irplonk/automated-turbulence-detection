# automated-turbulence-detection
Fall 2017-Spring 2018 Junior Design Project with Honeywell

## Release Notes - Version 1.0
#### New Features
* Flight paths are now displayed when the cursor hovers over a plane. Controlled via a new toggle
* Removed unnecessary imports matplotlib and numpy from simulation
* Map dynamically resizes to window updates to eliminate the gap between it and the help and toggle panel

#### Known Bugs
* Active flights located at (0.0, 0.0) in the simulation which do not update

## Installation Information

#### Pre-requisites
* [Python](https://www.python.org/) &ge; 3.6 with pip (comes with default Python installation), or another package management system. Dependency installation instructions will be written for pip
* Modern web browser. [Google Chrome](https://www.google.com/chrome/) is recommended for best performance

#### Dependencies
* [django](https://www.djangoproject.com/) &ge; 2.0.4 (`pip install django`)
* [netCDF4](http://unidata.github.io/netcdf4-python/) &ge; 1.3.1 (`pip install netcdf4`)
* [pytz](https://pypi.org/project/pytz/) &ge; 2018.4 (`pip install pytz`)
* [geopy](https://github.com/geopy/geopy) &ge; 1.13.0 (`pip install geopy`)
* [NumPy](http://www.numpy.org/) &ge; 1.14.2 (`pip install numpy`)
* [SciPy](https://www.scipy.org/) &ge; 1.14.2 (`pip install scipy`)
* [scikit-learn](http://scikit-learn.org/stable/) &ge; 0.19.1 (`pip install scikit-learn`)

#### Download
Download the project with a [direct link](https://github.com/iplonk3/automated-turbulence-detection/archive/master.zip) to a zip file, or by cloning the project using the command
```
git clone https://github.com/iplonk3/automated-turbulence-detection.git
```

#### Build
No manual building is necessary, all project files and dependencies will be compiled automatically upon launch

#### Installation
If the project zip file was downloaded, unzip the downloaded files

### Running

##### Starting the Application
To start the application, run the following command from the root of the project directory
```
python server/manage.py runserver
```
to start the server, and navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) with a web browser. This page shows active flights and turbulence reports on a map, and information about the turbulence reports and flights to be viewed by hovering over the reports or airplanes.

Raw flight and turbulence data from the database can be viewed in a table format at the URLs [http://127.0.0.1:8000/display?table=flights](http://127.0.0.1:8000/display?table=flights) and [http://127.0.0.1:8000/display?table=reports](http://127.0.0.1:8000/display?table=reports) respectively.

##### Simulation Control
* To control the simulation, navigate to [http://127.0.0.1:8000/simulation/](http://127.0.0.1:8000/simulation/). From here the simulation can be started, stopped, and paused
* The `flight_time` parameter controls how frequently in (simulated) seconds new flights will take off
* The `report_time` parameter controls how frequently in (simulated) seconds new weather reports will be generated
* The `update_time` parameter controls how frequently in (real) seconds the simulation will update the information in the database
* The `time_per_update` parameter controls how far the simulation will progress in (simulated) seconds every time the database is updated

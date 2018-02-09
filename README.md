# automated-turbulence-detection
Fall 2017-Spring 2018 Junior Design Project with Honeywell

### Set up
You must install `django-environ` to do this run the following line:
```
pip install django-environ
```
Then, create a file named `.env` which will look like this:
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
To run the application, run the following line in the server directory:
```
python manage.py runserver
```
and navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
If you make changes to any files while the server is running, it is not
necessary to restart it. All changes will be present once you reload the webpage.

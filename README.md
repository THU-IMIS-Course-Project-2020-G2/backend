# Base
This is a preliminary version of kitchen backend with full menu management systems.

To get started with the app, clone the repo and then install Python 3 and Django 3. There are also some python packages for you to download such as ```django-cors-headers``` and ```django-apscheduler```.

```
$ git clone https://github.com/THU-IMIS-Course-Project-2020-G2/Base.git
$ cd Base
```
You first need to create a database with the MySQL 8.0 Server.

```
create database g2
```

If you have created that database, there is no need to do that again.

Then you need to change the setting.py in the ```backend``` folder to your username and password.

Next, migrate the database:

```
$ python manage.py makemigrations
$ python manage.py migrate
```
And you need to load the four ```.sql``` files into that database. (If you have successfully loaded the dish files before, you only need to load ```all_order_log.sql``` and ```order_detail.sql```. The database is done then.

You can move your ```frontend``` folder into the outside ```frontend``` folder for test. Remember to change the templates DS_DIR in the ```setting.py``` and the ```url.py``` under the ```Base\backend\backend``` so that the http:127.0.0.1:8000/api should redirect to your ```index.html``` in your own frontend file  ```frontend\dist\index.html```. You can run the server below:
```
$ python manage.py runserver 
```

You can check the Tsinghua Cloud and Tencent docs for my up-to-date realized apis and corresponding parameters.

# Base
This is a preliminary version of kitchen backend with full menu management systems.

To get started with the app, clone the repo and then install Python 3 and Django 3. There are also some python packages for you to download such as ```django-cors-headers```, ```pulp```,```dicttoxml```,```xmltodict``` and ```django-apscheduler```.

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
And you need to load the four ```.sql``` files (excepte ```apscheduler.sql```) into that database. (If you have successfully loaded the dish files before, you only need to load ```all_order_log.sql``` and ```order_detail.sql```. The database is done then.

You can move your ```frontend``` folder into the outside ```frontend``` folder for test. Remember to change the password of your mysql in the ```setting.py```. You can run the server below:
```
$ python manage.py runserver 
```

You can check the Tsinghua Cloud and Tencent docs for my up-to-date realized apis and corresponding parameters.

## Note
The ```apschedule.sql``` only executes after the server has been terminated. It clears the apscheduler table so that we can use a new register job file next time.

The ```material.xml``` is used in the simulations for G2-G4 interactions.

The ```xml_to_dict.py``` and ```dicttoxml.py``` revised a little for the original python package ```xmltodict``` and ```dicttoxml``` so that it matches the format in https://www.convertjson.com/.

## Remind for myself 
The default port in this package is http://127.0.0.1:8080. To deploy in the Huawei Cloud Server managed by Prof. Hou, we still need to clear up some urls in ```manager/url.py```, which was used for simulating before.

Besides, the ```views_test.py``` and ```tests.py``` are used for simulation tests.

Another remind is that the ```json``` dict after resolution from ```xml``` is all dictionary. We might better change the necessary properties into int or float in case of troubles.
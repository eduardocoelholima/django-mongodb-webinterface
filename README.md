# django-mongodb-webinterface
Simple proof of concept Python/Django Web Interface to query a mongoDB instance

## Installation Instructions

The following steps were successfully tested on Ubuntu 15.10 x86 64bit, using Python 2.7.9, Django 1.7.9, Pymongo 3.0.3 and mongoDB 2.6.10.  These are the latest version available through Ubuntu repository as of 2015-12-07, but you should be good with a fairly recent installation of the required dependencies.

1. Before we actually install anything, let’s make sure your Ubuntu local apt repository is synced with the latest one. Open a terminal an type:
  ```
  sudo apt-get update
  ```
2. Now let’s install the required prerequisites using ubuntu built-in apt package manager
  ```
  sudo apt-get install python-pymongo python-django
  ```
3. Download the latest version of the code
  ```
  sudo wget https://github.com/eduardocoelholima/django-mongodb-webinterface/archive/master.zip
  ```
4. Unzip the code whereever you want. You can run the code in any directory you which thanks to Python and Django awesome modularity. From this point let's assume you are running from your Downloads directory.
  ```
  cd ~/Downloads
  unzip https://github.com/eduardocoelholima/django-mongodb-webinterface/archive/master.zip
  ```
5. Run the local webserver
  ```
  cd ~/Downloads/django-mongodb-webinterface/
  python manage.py runserver
  ```
6. Open the browser
  ```
  firefox http://localhost/polls
  ```
7. Done! Easy, right?

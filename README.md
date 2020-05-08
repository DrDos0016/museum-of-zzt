# Museum of ZZT

## Installation And Initial Setup

### Prerequisites

* Python 3.7.5 or newer
* MariaDB (or MySQL)

1. Clone Repo: `git clone https://github.com/DrDos0016/museum-of-zzt.git`
2. Create Python3 virtural environment: `python3 -m venv venv`
3. Activate the virtual envrionment: `source venv/bin/activate`
4. Update pip: `pip install --upgrade pip`
5. Download libraries from requirements.txt: `pip install -r requirements.txt`
6. Create your private settings file (see Non-Repository Content section)
7. Create the database in MariaDB/MySQL: `CREATE DATABASE museum_of_zzt`
8. Import the repo's provided database dump: `python3 tools/import_database.py museum_repo_db.sql`
9. Run the Django development server: `python3 manage.py runserver`
10. The site should be running at [127.0.0.1:8000](http://127.0.0.1:8000) albeit without static files like CSS and images.
11. Enable debug mode.

### Debug mode

Django's DEBUG setting in museum/settings.py looks for a file called "DEV" in
the project's root directory. If it finds this file, DEBUG will be True.
You'll need to create this file or manually set this variable in order to allow
Django to serve static assets.

## Unfriendly Decisions

While the main site is properly able to run in whatever directory you choose, the tools folder is loaded with files that assume the repository is located in "/var/projects/museum".

Almost, one exception as I type this up to fix later: museum_site/urls.py has the path hardcoded at the very end for serving the /zgames/ directory in the development server. This
needs to be changed in order to download/play files.

Sorry!

## Non-Repository Content

I generally avoid including *binary* content in the Museum repository which isn't in some way "mine".
As such, the following features are deliberately missing by default:

### museum/private.py

This file contains the DATABASES and SECRET_KEY variables used by Django. You'll need to specify the backend, database name, and login credentials.
[Django Settings Documentation](https://docs.djangoproject.com/en/3.0/ref/settings/) will provide examples. A (irregularly updated) dump of the database
in included for MariaDB/MySQL.

### /zgames/

This is the folder which contains all the ZZT (related) files hosted on the Museum.

Use wget to obtain these files (from the project root): `wget -m -np -nH -R "index.html*" "https://museumofzzt.com/zgames/"`

### Comics

These are the images used for the ZZTer comics section of the site.

Using wget to obtain these images (from project_root/comic): `wget -m -np -nH -R "index.html*" "https://museumofzzt.com/static/comic/"`

### Zeta

Zeta is an emulator to run ZZT on modern machines as well as in the browser. Asie maintains a fork specifically designed for integration with the Museum which is a submodule to the Museum repo.

Firstly acquire the Museum Zeta build for the repo: `git submodule update --init --recursive`

Then acquire the various engies which Zeta can run using wget (from project_root/museum_site): `wget -m -np -nH -R "index.html*" "https://museumofzzt.com/static/data/zeta86_engines/"`

### Zookeeper

Zookeeper is a Python library I have written to help parse ZZT files in Python. It is technically an optional component for the site, but without it the "Set Screenshot" web tool
and the Worlds of ZZT Twitter Bot (and likely some other random things) will not function. You can get Zookeeper from its [repository](https://github.com/DrDos0016/zookeeper). It may
either be installed with `python setup.py install`, or the zookeeper module folder with the repository can be copied and pasted into the root of this repository.

Keep in mind, if you install it, Zookeeper will show up when running `pip freeze`. If you try to install Zookeeper via pip, you will get a different library that has nothing to do
with ZZT and make some issues for yourself.

### Twitter bot

tools/crons/private.py needs to have Twitter API credentials as well as Zookeeper.

### Discord Bot

The Worlds of ZZT Discord bot requires a token to authenticate itself. Create a file `discord/private.py` and include a variable named `TOKEN` with your token to run the bot.

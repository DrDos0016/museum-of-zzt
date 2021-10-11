# Museum of ZZT

## Installation And Initial Setup

These instructions were based on the experience of setting up a development
environment in October 2021. They can definitely be made friendlier. My
apologies.

## Prerequisites

* Python 3.8.10 or newer (or potentially older)
* MariaDB (or MySQL)

1. Clone Repo: `git clone https://github.com/DrDos0016/museum-of-zzt.git`
. In the repository's root directory, create Python3 virtural environment: `python3 -m venv venv`
. Activate the virtual envrionment: `source venv/bin/activate`
. Update pip: `pip install --upgrade pip`
. Download libraries from requirements.txt: `pip install -r requirements.txt`
. (You may need to install the package "libmariadb-dev-compat")
. If you get an error about conflicting requirements, install idna and requests via `pip install idna`, `pip install requests`, and then comment out the line in requirements.txt for `idna`.
. Copy the `museum/example-private.py` settings file to `museum/private.py` and configure your database settings and secret key  (see Non-Repository Content section)
. Copy the `museum_site/example-private.py` settings file to `museum_site/private.py` and configure any site settings to your environment if needed (see Non-Repository Content section)
. Install the Zookeeper ZZT Python library version 1. Clone the repository `git clone https://github.com/DrDos0016/zookeeper.git` and copy the `zookeeper` directory into the project root or symlink it as appropriate.
. Mark your development environment as such by creating a file in the project root named `DEV`
. Create the database in MariaDB/MySQL: `CREATE DATABASE museum_of_zzt`
. Import the repo's provided database dump: `python3 tools/import_database.py museum_repo_db.sql`
. Run any database migrations `python3 manage.py migrate`
. Run the Django development server: `python3 manage.py runserver`
. The site should be running at [127.0.0.1:8000](http://127.0.0.1:8000)

## Using Tools

Several older (and some newer) Python scripts in the tools directory have hardcoded paths to `/var/projects/museum-of-zzt` or `/var/projects/museum`.

These are slowly being transitioned to a more agnostic setup to allow the Museum to run from any directory. In the meantime, it can be helpful to set the environment variables `PYTHONPATH` and `DJANGO_SETTINGS_MODULE` in your virtual environment. Depending on how you start your development server you may want to find a place to automatically set these variables.

## Non-Repository Content

I generally avoid including *binary* content in the Museum repository which isn't in some way "mine".
As such, the following features are deliberately missing by default:

### /zgames/

This directory contains all the ZZT (related) files hosted on the Museum.

Use wget to obtain these files (from the project root): `wget -m -np -nH -R "index.html*" "https://museumofzzt.com/zgames/"`

### Comics

These are the images used for the ZZTer comics section of the site.

Using wget to obtain these images (from project_root/comic): `wget -m -np -nH -R "index.html*" "https://museumofzzt.com/static/comic/"`

### Zeta

Zeta is an emulator to run ZZT on modern machines as well as in the browser. Asie maintains a fork specifically designed for integration with the Museum which is a submodule to the Museum repo.

Firstly acquire the Museum Zeta build for the repo: `git submodule update --init --recursive`

Then acquire the various engies which Zeta can run using wget (from project_root/museum_site): `wget -m -np -nH -R "index.html*" "https://museumofzzt.com/static/data/zeta86_engines/"`

### Twitter bot

`tools/crons/private.py` needs to have Twitter API credentials as well as Zookeeper.

### Discord Bot

The Worlds of ZZT Discord bot requires a token to authenticate itself. Create a file `discord/private.py` and include a variable named `TOKEN` with your token to run the bot.

### Django Admin

The Django administration (accessible at /admin) requires that a user with access to it exists. One can be created from the commandline with `python manage.py createsuperuser`. If you are using the included database dump, there should be a user named "admin" with a password of "password" that is already marked as one.

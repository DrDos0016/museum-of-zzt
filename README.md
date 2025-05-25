# Museum of ZZT

The Museum of ZZT is a Django-powered website created as a public archive of ZZT worlds and ephemera.

## Prerequisites

* Python 3.8.10 or newer
* MariaDB/MySQL if you wish to use the repository's included database dump

## Installation And Initial Setup

1. Clone the repository: `git clone https://github.com/DrDos0016/museum-of-zzt.git`.
2. In the repository's root directory, create a Python3 virtual environment: `python3 -m venv venv`.
3. Activate the virtual environment: `source venv/bin/activate`.
4. Download libraries from requirements.txt: `pip install -r requirements.txt`.
5. Create the database in MariaDB/MySQL: `CREATE DATABASE museum_of_zzt`. Django supports other database engines, but the public copies of the database are designed for these engines. `museum_of_zzt` is the default, though you can set the environment variable `MOZ_DB_NAME` to whatever you wish to call your database.
6. Configure any environment variables that need to be changed for your environment (see Environment Variables section). You will need `PYTHONPATH` to be set to the directory the repository was cloned into and the path to the sites-packages directory of your virtual environment. Django also needs to know what settings to use by default which can be done by setting `DJANGO_SETTINGS_MODULE="museum.settings"`. Database credentials will likely be required, while most other settings have fall-backs that will work fine in a development environment. By default, keys for external services such as posting to social media sites will be set to invalid values that allow the site to successfully start, but will cause those functions to fail. You must supply your own keys for these functions.
7. Import the database dump provided in the repository: `python3 tools/import_database.py museum_repo_db.sql`. This is technically optional, but there are no promises many site features will function with an empty database.
8. Create the cache table: `python manage.py createcachetable`
9. Run any database migrations created since the last time the repository's database dump has been updated `python3 manage.py migrate`.
10. Install the Zookeeper ZZT Python library version 1. Clone the repository `git clone https://github.com/DrDos0016/zookeeper.git` and copy the `zookeeper` directory into the project root or symlink it as appropriate.
11. Run the Django development server: `python3 manage.py runserver`. The site should now be running at [127.0.0.1:8000](http://127.0.0.1:8000).

## Environment Variables

Many private settings are stored using environment variables with placeholder defaults available to allow the site to function in a development environment. Most are used in `museum/settings.py` and imported from there when needed. More notable ones include:

* `PYTHONPATH` - Extra path used to search for Python modules. Should be set the project root as well as the virtual environment's site-packages.
* `DJANGO_SETTINGS_MODULE` - Location of the Museum's Django settings file. This should always be `museum.settings`.
* `MOZ_ENVIRONMENT` - What type of environment the site is running in. Can be `DEV`, `BETA`, or `PROD`.
* `MOZ_DB_NAME` - The name of the database used by the site (default: `museum_of_zzt`)
* `MOZ_DB_USER` - The username that will connect to the database (default: `root`)
* `MOZ_DB_PASS` - The password used to connect to the database (default: `<empty_string>`)
* `MOZ_SECRET_KEY` - The Secret Key used by django (default: `!c;LOCKED FILE`). If this key is detected on startup a message is produced telling you to change this before moving to a non-development environment. If this key is detected in a non-development environment, the startup process will stop itself from proceeding.
* `MOZ_UNREGISTERED_SUPPORTERS_FILE` - A path used to a json file to display Patrons on the site credits page (default: `None`). If this value has not been set, the site credits page will only display registered users marked as patrons. This value is read in `museum_site/views.py`.

Several more settings exist not mentioned above. Their names and default values may be found in `settings.py` for both the project ("museum") as well as applications ("museum_site") that make up the repository.

## Using Tools

Several older Python scripts in the tools directory have hard-coded paths to `/var/projects/museum-of-zzt` or `/var/projects/museum`.

These are slowly being transitioned to a more agnostic setup to allow the Museum to run fully regardless of installation directory. In the meantime, it can be helpful to set the environment variables `PYTHONPATH` and `DJANGO_SETTINGS_MODULE` in your virtual environment. Depending on how you start your development server you may want to find a place to automatically set these variables.

## Requirements (short list)

The file `requirements.txt` is generated with `pip freeze` which has amassed some clutter with various requirements of different social media libraries. This list covers the Python libraries used by the Museum of ZZT as one would directly install from pip.

* `atproto` - Bluesky API integration
* `beautifulsoup4` - Staff-only article functions
* `discord.py` - Discord Bot
* `django` - Web framework for the Museum of ZZT website
* `gunicorn` - Webserver
* `internetarchive` - Mirroring files to the Internet Archive
* `markdown` - Formatting user-written data
* `Mastodon.py` - Mastodon API integration
* `mysqlclient` - Database connectivity
* `pillow` - Preview image generation
* `pytumblr` - tumblr API integration
* `requests` - POSTs to Discord webhooks
* `tweepy` - Twitter API integration

## Non-Repository Content

I generally avoid including *binary* content in the Museum repository which isn't in some way "mine". As such, the following features are deliberately missing by default:

### /zgames/

This directory contains all the ZZT (related) files hosted on the Museum.

Use wget to obtain these files (from the project root): `wget -m -np -nH -R "index.html*" "https://museumofzzt.com/zgames/"`

### Comics

These are the images used for the ZZTer comics section of the site.

Using wget to obtain these images (from the project root): `wget -m -np -nH -R "index.html*" "https://museumofzzt.com/static/comic/"`

### Zeta

Zeta is an emulator to run ZZT on modern machines as well as in the browser. Asie maintains a fork specifically designed for integration with the Museum which is a submodule to the Museum repo.

Firstly acquire the Museum Zeta build for the repo: `git submodule update --init --recursive`

Then acquire the various engines which Zeta can run using wget (from project_root/museum_site): `wget -m -np -nH -R "index.html*" "https://museumofzzt.com/static/data/zeta86_engines/"`

### Twitter bot

`tools/crons/private.py` needs to have Twitter API credentials as well as Zookeeper.

### Discord Bot

The Worlds of ZZT Discord bot requires a token to authenticate itself. Create a file `discord/private.py` and include a variable named `TOKEN` with your token to run the bot.

### Django Admin

The Django administration (accessible at /admin) requires that a user with access to it exists. One can be created from the command line with `python manage.py createsuperuser`. If you are using the included database dump, there should be a user named "admin" with a password of "password" that is already marked as one. (No, those credentials will not work on the actual site.)

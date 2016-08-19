# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from django import VERSION
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db import connection
from django.db.models import Count, Avg, Sum, Q
from django.core.exceptions import ValidationError
#from django.utils.timezone import utc
#from django.contrib.auth import logout, authenticate, login as auth_login

from z2_site.models import *
from datetime import datetime
from random import randint
import math, zipfile, glob, os, sys

ADS = True #Adsense
TRACKING = True #Analytics

SITE_ROOT       = "/var/projects/z2/"
ZZT2PNG_TEMP    = "/var/projects/z2/assets/data/temp/"
ZZT2PNG_PATH    = "/var/projects/z2/tools/zzt2png.py"

PAGE_SIZE       = 25
UPLOAD_CAP      = 1048576 # 1 Megabyte

PYTHON_VERSION  = sys.version
DJANGO_VERSION  = VERSION

print("Python:", PYTHON_VERSION)
print("Django:", DJANGO_VERSION)

GENRE_LIST = ["Action", "Adventure", "Alternative", "Arcade", "Art", "Cameo", "Catalog", "Cinema", "Comedy", "Compilation", "Demo", "Dungeon", "Edutainment", "Engine", "Erotic", "Fantasy", "Help", "Horror", "Incomplete", "Magazine", "Maze", "Minigame", "Multiplayer", "Music", "Mystery", "Other", "Parody", "Philosophy", "Platformer", "Puzzle", "Racing", "Random", "Remake", "RPG", "Sci-Fi", "Shooter", "Simulation", "Sports", "Strategy", "Toolkit", "Trippy", "Trivia", "Tutorial"]
DETAIL_LIST = ("MS-DOS", "Windows 16-bit", "Windows 32-bit", "Windows 64-bit", "Linux", "OSX", "Featured", "Contest", "Soundtrack", "Font", "Hack")


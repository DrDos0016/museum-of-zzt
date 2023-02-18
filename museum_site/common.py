from django.shortcuts import redirect, reverse

from museum_site.models import *
from museum_site.constants import *

from datetime import datetime
import codecs
import urllib.parse


def record(*args, **kwargs):
    if not os.path.isfile("/var/projects/museum-of-zzt/PROD"):
        print(*args, **kwargs)

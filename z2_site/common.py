from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Count, Avg, Sum, Q
from django.core.exceptions import ValidationError
#from django.utils.timezone import utc
#from django.contrib.auth import logout, authenticate, login as auth_login

from z2_site.models import *
from datetime import datetime
from random import randint
import math, zipfile, glob

ADS = True #Adsense
TRACKING = True #Analytics

DETAIL_LIST = ("MS-DOS", "Windows 16-bit", "Windows 32-bit", "Windows 64-bit", "Linux", "OSX", "Featured", "Contest", "Soundtrack", "Font", "Hack")
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.db.models import Count, Avg, Sum, Q
#from django.utils.timezone import utc
#from django.contrib.auth import logout, authenticate, login as auth_login

from z2_site.models import *

ADS = True #Adsense
TRACKING = True #Analytics

def browse(request, letter="*"):
    data = {}
    data["games"] = range(0,10)
    return render_to_response("browse.html", data)

def index(request):
    data = {}
    return render_to_response("index.html", data)
    

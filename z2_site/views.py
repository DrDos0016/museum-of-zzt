from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Count, Avg, Sum, Q
#from django.utils.timezone import utc
#from django.contrib.auth import logout, authenticate, login as auth_login

from z2_site.models import *
from datetime import datetime

import math, zipfile, glob

ADS = True #Adsense
TRACKING = True #Analytics

def article_directory(request):
    data = {}
    return render_to_response("article_directory.html", data)
    
def article_view(request, id):
    id = int(id)
    data = {"id":id}
    data["article"] = get_object_or_404(Article, pk=id)
    data["title"] = data["article"].title
    return render_to_response("article_view.html", data)

def browse(request, letter="*", page=1):
    data = {}
    data["page"] = int(request.GET.get("page", page))
    data["letter"] = letter if letter != "1" else "#"
    data["files"] = File.objects.filter(letter=letter)[(data["page"]-1)*10:data["page"]*10]
    data["count"] = File.objects.filter(letter=letter).count()
    data["pages"] = int(math.ceil(data["count"] / 10.0))
    data["page_range"] = range(1, data["pages"] + 1)
    data["prev"] = max(1,data["page"] - 1)
    data["next"] = min(data["pages"],data["page"] + 1)
    return render_to_response("browse.html", data)

def file(request, letter, filename):
    data = {}
    data["file"] = get_object_or_404(File, letter=letter, filename=filename)
    data["letter"] = letter
    zip = zipfile.ZipFile("/var/projects/misc/zzt_release/zgames/"+filename) # TODO Proper path + os.path.join()
    data["files"] = zip.namelist()
    data["files"].sort()
    return render_to_response("file.html", data)

def index(request):
    data = {}
    return render_to_response("index.html", data)
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Count, Avg, Sum, Q
#from django.utils.timezone import utc
#from django.contrib.auth import logout, authenticate, login as auth_login

from z2_site.models import *
from datetime import datetime

import zipfile, binascii

def get_zip_file(request):
    data = {}
    letter = request.GET.get("letter")
    zip = request.GET.get("zip")
    filename = request.GET.get("filename", "")
    ext = filename.split(".")[-1].lower()
    
    try:
        zip = zipfile.ZipFile("/var/projects/z2/zgames/"+letter+"/"+zip) # TODO Proper path + os.path.join()
        file = zip.open(filename)
        
        if ext in ["txt", "bat"]:
            return HttpResponse(file.read().replace("\r\n", "<br>").replace("\r", "<br>").replace("\n", "<br>"))
        if ext in ["hi"]:
            return HttpResponse(file.read().replace("\r\n", "<br>").replace("\r", "<br>").replace("\n", "<br>"))
        if ext == "zzt":
            return HttpResponse(binascii.hexlify(file.read()))
        else:
            return HttpResponse("Maybe in the future")
    except:
        return HttpResponse("An error occurred, and the file could not be retreived.")
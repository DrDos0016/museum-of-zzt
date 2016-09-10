# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Count, Avg, Sum, Q
#from django.utils.timezone import utc
#from django.contrib.auth import logout, authenticate, login as auth_login

from z2_site.models import *
from datetime import datetime

import zipfile, binascii
import base64

def get_zip_file(request):
    data = {}
    letter = request.GET.get("letter")
    zip = request.GET.get("zip")
    filename = request.GET.get("filename", "")
    ext = filename.split(".")[-1].lower()
    
    try:
        zip = zipfile.ZipFile("/var/projects/z2/zgames/"+letter+"/"+zip) # TODO Proper path + os.path.join()
        file = zip.open(filename)
        
        if ext in ("txt", "bat", "cfg"):
            return HttpResponse(file.read().decode("utf-8").replace("\r\n", "<br>").replace("\r", "<br>").replace("\n", "<br>"))
        elif ext in ("hi", "zzt"):
            return HttpResponse(binascii.hexlify(file.read()))
        elif ext in ("jpg", "jpeg", "bmp", "gif", "png"):
            b64 = base64.b64encode(file.read())
            return HttpResponse(b64)
        elif ext in ("wav", "mp3", "ogg", "mid", "midi"):
            response = HttpResponse(file.read())
            
            if ext == "wav":
                response["Content-Type"] = "audio/wav wav"
            elif ext == "mp3":
                response["Content-Type"] = "audio/mpeg mp3"
            elif ext == "ogg":
                response["Content-Type"] = "audio/ogg ogg"
            else: # Fallback
                response["Content-Type"] = "application/octet-stream"
            
            return response
        else:
            return HttpResponse("Maybe in the future")
    except:
        return HttpResponse("An error occurred, and the file could not be retreived.")
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Count, Avg, Sum, Q
#from django.utils.timezone import utc
#from django.contrib.auth import logout, authenticate, login as auth_login

from .models import *
from .common import *

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
        zip = zipfile.ZipFile(os.path.join(SITE_ROOT, "zgames", letter, zip)) # TODO Proper path + os.path.join()
        file = zip.open(filename)
    except Exception as error:
        print(type(error))
        print(error)
        return HttpResponse("An error occurred, and the file could not be retreived.")
        
    if ext in ("txt", "bat", "cfg", "nfo"):
        output = file.read()
        try:
            output = output.decode("utf-8")
            encoding = "utf-8"
        except UnicodeDecodeError:
            output = output.decode("cp437")
            encoding = "cp437"
        output = output.replace("\r\n", "<br>").replace("\r", "<br>").replace("\n", "<br>").replace("  ", " &nbsp;")
        output = "<div class='" + encoding + "'>" + output + "</div>"
        
        return HttpResponse(output)
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

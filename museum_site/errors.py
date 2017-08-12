from django.shortcuts import render
from .common import *

def raise_error(request, status):
    try:
        status = int(status)
    except ValueError:
        status = 404

    if status == 400:
        return bad_request_400(request)
    elif status == 403:
        return permission_denied_403(request)
    elif status == 500:
        return server_error_500(request)
    else:
        return page_not_found_404(request)

def bad_request_400(request):
    data = {"title": "Bad Request",
    "msg": "The request sent to the server was invalid."}
    return render(request, "museum_site/error.html", data)

def permission_denied_403(request):
    data = {"title": "Forbidden",
    "msg": "The content you were trying to access is restricted."}
    return render(request, "museum_site/error.html", data)

def page_not_found_404(request):
    data = {"title": "Page Not Found",
    "msg": "The content you were trying to access could not be found."}
    return render(request, "museum_site/error.html", data)

def server_error_500(request):
    data = {"title": "Internal Server Error",
    "msg": "The server was unable to process your request."}
    return render(request, "museum_site/error.html", data)

from django.shortcuts import render
from .common import *
from .constants import *
from .models import *


def user_data(request):
    data = {"title": "User Data"}
    excluded_keys = [
        "_auth_user_id",
        "_auth_user_backend",
        "_auth_user_hash",
    ]

    if request.GET.get("delete") and request.GET["delete"] not in excluded_keys:
        del request.session[request.GET["delete"]]

    data["user_data"] = []
    for k, v in request.session.items():
        if k not in excluded_keys:
            data["user_data"].append((k, v))

    return render(request, "museum_site/user_data.html", data)

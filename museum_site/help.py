from django.shortcuts import render
from .common import *
from .constants import *
from .models import *

def genres(request):
    data = {}

    return render(request, "museum_site/help/genres.html", data)

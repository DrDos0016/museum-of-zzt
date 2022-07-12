from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from museum_site.common import *
from museum_site.constants import *
from museum_site.models import *


def test(request):
    data = {}

    data["detail_filter"] = Detail.objects.filter(visible=True).values("pk", "title")
    data["years"] = [str(x) for x in range(1991, YEAR + 1)]

    return render(request, "museum_api/v2/test.html", data)

def help(request):
    data = {}
    return render(request, "museum_api/v2/help.html", data)

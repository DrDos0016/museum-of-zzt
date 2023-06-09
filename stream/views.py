from datetime import datetime

from django.shortcuts import render

from museum_site.core.transforms import qs_manual_order
from museum_site.models import File

# Create your views here.
def index(request):
    context = {"title": "Streamy"}
    return render(request, "stream/index.html", context)


def title_screen_background(request):
    context = {}

    seed = request.GET.get("seed", str(datetime.now()))
    qs = File.objects.roulette(seed, 101).order_by("id")
    context["qs"] = qs
    return render(request, "stream/title-screen-background.html", context)


def overview(request):
    context = {}
    context["zfiles"] = qs_manual_order(File.objects.filter(pk__in=request.GET.getlist("pk")), request.GET.getlist("pk"))
    return render(request, "stream/overview.html", context)

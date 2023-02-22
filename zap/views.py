from django.shortcuts import render

from .forms import *
from .core import *

def index(request):
    context = {"title": "ZAP"}
    initial_form_data = None

    if request.method == "POST":
        form = ZAP_Form(request.POST, request.FILES)
    else:
        form = ZAP_Form(initial_form_data)


    context["form"] = form
    return render(request, "zap/zap.html", context)

def prefab_form(request, form_key):
    context = {"title": "ZAP - Prefab"}
    form = get_zap_form(request, form_key)

    if request.method == "POST":
        if form.is_valid():
            form.process(request)

    context["form"] = form
    return render(request, "zap/stream-schedule-form.html", context)


def preview(request, form_key):
    context = {}
    if form_key == "stream-schedule":
        raw = request.POST.copy()
        for k, v in raw.items():
            context[k] = v
        print(context)
        return render(request, "zap/subtemplate/stream-schedule.html", context)

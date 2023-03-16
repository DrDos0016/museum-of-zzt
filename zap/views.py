import base64
import glob
import json
import os

from datetime import datetime, timezone

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render

from museum_site.constants import SITE_ROOT
from .forms import *
from .core import ZAP_UPLOAD_PATH, ZAP_STATIC_PATH


@staff_member_required
def stream_schedule_create(request):
    context = {"title": "Create Stream Schedule"}
    return prefab_form(request, ZAP_Create_Stream_Schedule_Form)


@staff_member_required
def index(request):
    context = {"title": "ZAP"}
    events = Event.objects.all().order_by("-pk")[:25]

    today = datetime.now(tz=timezone.utc)
    raw_uploads = glob.glob(os.path.join(ZAP_UPLOAD_PATH, str(today.year), ("0" + str(today.month))[-2:], "*"))
    context["recent_uploads"] = []
    for u in raw_uploads:
        context["recent_uploads"].append(u[u.find("/static/"):])

    context["current_month_path"] = os.path.join(ZAP_STATIC_PATH, str(today.year), ("0" + str(today.month))[-2:])
    context["last_month_path"] = ""

    context["events"] = events
    return render(request, "zap/index.html", context)


@staff_member_required
def media_upload(request):
    return prefab_form(request, ZAP_Media_Upload_Form)


@staff_member_required
def prefab_form(request, form):
    context = {"title": "ZAP - Prefab"}

    if request.method == "POST":
        form = form(request.POST, request.FILES)
        if form.is_valid():
            form.process(request)
    else:
        initial = None
        if request.GET.get("pk"):
            event = Event.objects.get(pk=request.GET["pk"])
            initial = json.loads(event.json_str)
        form = form(initial)
        if not initial and hasattr(form, "smart_start"):
            form.smart_start()

    context["form"] = form
    return render(request, "zap/{}".format(form.template_name), context)


@staff_member_required
def preview(request, form_key):
    context = {}
    if form_key == "stream-schedule":
        raw = request.POST.copy()
        for k, v in raw.items():
            context[k] = v
        print(context)
        return render(request, "zap/subtemplate/stream-schedule.html", context)


@staff_member_required
def view_event(request, pk):
    context = {"title": "ZAP - View Event - {}"}

    event = Event.objects.get(pk=pk)

    context["title"] = context["title"].format(event.title)
    context["event"] = event
    return render(request, "zap/view-event.html", context)


@staff_member_required
def save_image_render(request):
    zap_static_root = os.path.join(SITE_ROOT, "museum_site", "static", "zap")
    zap_renders_path = os.path.join(zap_static_root, "renders")
    event = Event.objects.get(pk=request.POST["pk"])
    raw = request.POST["image_data"][22:]  # Strip image identifier and only store raw data
    image_data = base64.b64decode(raw)

    file_name = "event-{}-image-render.png".format(event.pk)

    # Save the image data
    with open(os.path.join(zap_renders_path, file_name), "wb") as fh:
        fh.write(image_data)

    # Log the render
    now = datetime.now(timezone.utc)
    event.image_render_datetime = now
    event.save()

    return HttpResponse("Saved {} at {}".format(file_name, str(now)[:19]))


@staff_member_required
def post_create(request):
    context = {"title": "ZAP - Create Post"}
    if request.GET.get("pk"):
        event = Event.objects.get(pk=request.GET.get("pk"))
    else:
        event = None


    if request.method == "POST":
        form = ZAP_Post_Form(request.POST)
        if form.is_valid():
            form.process(request)
    else:
        form = ZAP_Post_Form()
        if event:
            form.smart_start(event)

    context["form"] = form
    context["event"] = event
    return render(request, "zap/create-post.html", context)


@staff_member_required
def post_boost(request):
    context = {"title": "ZAP - Boost Post"}

    if request.method == "POST":
        form = ZAP_Post_Boost_Form(request.POST)
        if form.is_valid():
            form.process(request)
    else:
        form = ZAP_Post_Boost_Form()

    context["form"] = form
    return render(request, "zap/boost-post.html", context)

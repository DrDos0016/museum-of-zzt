import base64
import glob
import json
import os
import re

from datetime import datetime, timezone

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import include

from museum_site.constants import SITE_ROOT
from museum_site.core.redirects import redirect_with_querystring
from museum_site.core.transforms import qs_manual_order
from museum_site.models import Article, File
from .forms import *
from .core import ZAP_UPLOAD_PATH, ZAP_STATIC_PATH


@staff_member_required
def index(request):
    context = {"title": "ZAP"}
    all_zap_url_patterns = include("zap.urls")[0].urlpatterns
    filtered_url_patterns = []
    for p in all_zap_url_patterns:
        if "<" in str(p.pattern) or "ajax" in str(p.pattern):  # Skip patterns with arguments or AJAX
            continue
        title = p.name.replace("_", " ").title()
        if title == "Zap Index":
            title = "ZAP"
        if title.startswith("Zap "):
            title = title[4:]
        filtered_url_patterns.append({"name": p.name, "title": title})
    context["zap_url_patterns"] = filtered_url_patterns
    events = Event.objects.all().order_by("-pk")[:25]
    posts = Post.objects.all().order_by("-pk")[:25]

    today = datetime.now(tz=timezone.utc)
    raw_uploads = glob.glob(os.path.join(ZAP_UPLOAD_PATH, str(today.year), ("0" + str(today.month))[-2:], "*"))
    context["recent_uploads"] = []
    for u in raw_uploads:
        context["recent_uploads"].append(u[u.find("/static/"):])

    context["current_month_path"] = os.path.join(ZAP_STATIC_PATH, str(today.year), ("0" + str(today.month))[-2:])
    context["last_month_path"] = ""

    context["events"] = events
    context["posts"] = posts
    return render(request, "zap/index.html", context)


@staff_member_required
def media_upload(request):
    return prefab_form(request, ZAP_Media_Upload_Form)


@staff_member_required
def create_publication_pack_post(request):
    context = {"title": "ZAP - Create Publication Pack Post"}

    if not request.GET.get("model"):
        form = ZAP_Model_Select_Form(queryset=Article.objects.filter(category="Publication Pack"))
    elif request.method == "POST":
        form = ZAP_Publication_Pack_Form(request.POST)
    else:
        form = ZAP_Publication_Pack_Form()

    context["form"] = form
    return render(request, "zap/create-publication-pack-post.html", context)


@staff_member_required
def prefab_form(request, form):
    context = {"title": "ZAP - {}"}

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
    context["title"] = context["title"].format(form.heading if hasattr(form, "heading") else "NO HEADING")
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

    if request.POST.get("filename"):
        file_name = request.POST.get("filename")
        event = None
    else:
        event = Event.objects.get(pk=request.POST["pk"])
        idx = request.POST["idx"]
        file_name = "event-{}-image-render-{}.png".format(event.pk, idx)

    raw = request.POST["image_data"][22:]  # Strip image identifier and only store raw data
    image_data = base64.b64decode(raw)

    # Save the image data
    with open(os.path.join(zap_renders_path, file_name), "wb") as fh:
        fh.write(image_data)

    now = datetime.now(timezone.utc)

    # Log the render
    if event:
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
    if not request.GET.get("pk"):
        return redirect_with_querystring("zap_post_select", "next=" + request.path)
    context = {"title": "ZAP - Boost Post"}
    post = Post.objects.get(pk=request.GET["pk"])

    if request.method == "POST":
        form = ZAP_Post_Boost_Form(request.POST)
        if form.is_valid():
            form.process(request)
    else:
        initial_values = {"accounts": post.posted_where(), "post_id": post.pk}
        form = ZAP_Post_Boost_Form(initial=initial_values)

    context["form"] = form
    context["post"] = post
    return render(request, "zap/boost-post.html", context)


def post_reply(request):
    context = {"title": "ZAP - Reply To Post"}
    if request.GET.get("pk"):
        post = Post.objects.get(pk=request.GET.get("pk"))
    else:
        post = None

    if request.method == "POST":
        form = ZAP_Reply_Form(request.POST)
        if form.is_valid():
            form.process(request)
    else:
        form = ZAP_Reply_Form()
        if post:
            form.smart_start(post)

    context["form"] = form
    context["post"] = post
    return render(request, "zap/create-post.html", context)


def post_select(request):
    context = {"title": "Select a Post!"}
    context["posts"] = Post.objects.all().order_by("-id")
    return render(request, "zap/post-select.html", context)


@staff_member_required
def share_publication_pack(request):
    context = {"title": "Publication Pack - Share"}

    if not request.GET.get("pk"):
        context["next"] = request.path
        context["articles"] = Article.objects.publication_packs()
        return render(request, "zap/article-select.html", context)
    else:
        article = Article.objects.get(pk=request.GET["pk"])

        all_matches = re.findall("{%.*model_block.*%}", article.content)
        zfile_ids = []
        for m in all_matches:
            if "view=" in m or "gallery" in m:  # Use the gallery frame to get IDs
                zfile_ids.append(re.sub(r"\D", "", m[:m.find("%}")]))  # Just the PK used in the template tag

        zfiles = qs_manual_order(File.objects.filter(pk__in=zfile_ids), zfile_ids)

        context["article"] = article
        context["zfiles"] = zfiles
        context["article_title"] = article.title.split("-")[2]
        context["vol"] = article.title.split("-")[1]
    return render(request, "museum_site/tools/share-publication-pack-redux.html", context)

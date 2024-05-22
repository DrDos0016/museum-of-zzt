import json
import math
import os
import re

from datetime import datetime

from django.db.models import Count
from django.db.models.functions import ExtractYear
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.defaultfilters import slugify
from django.views.generic import TemplateView

from museum_site.core.detail_identifiers import *
from museum_site.constants import ZGAMES_BASE_PATH
from museum_site.forms.zfile_forms import View_Explicit_Content_Confirmation_Form
from museum_site.forms.wozzt_forms import WoZZT_Roll_Form
from museum_site.models import Article, Author, Company, Genre, Profile, Review, WoZZT_Queue
from museum_site.models import File as ZFile
from museum_site.settings import DISCORD_INVITE_URL, PASSWORD5DOLLARS


class Museum_Base_Template_View(TemplateView):
    def get_title(self):
        return self.title if self.title else ""

    def get_meta_context(self):
        return {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.get_title()
        return context

    def render_to_response(self, context, **response_kwargs):
        if hasattr(self, "redirect_to"):
            return redirect(self.redirect_to)
        return super().render_to_response(context, **response_kwargs)


class Ascii_Reference_View(Museum_Base_Template_View):
    title = "Ascii Character Reference"
    template_name = "museum_site/ascii-reference.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["range"] = list(range(0, 256))
        context["scale"] = 2
        context["orientation"] = "horiz"
        context["meta_context"] = {
            "description": ["name", "A reference page for the ASCII characters used by ZZT"],
            "og:title": ["property", context["title"] + " - Museum of ZZT"],
            "og:image": ["property", "pages/ascii-reference.png"]
        }
        return context


class Discord_Overview_View(Museum_Base_Template_View):
    title = "Joining The Worlds of ZZT Discord"
    template_name = "museum_site/discord.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meta_context"] = {
            "description": ["name", "Rules, information, and an invite link to the Worlds of ZZT Discord server"],
            "og:title": ["property", context["title"] + " - Museum of ZZT"],
            "og:image": ["property", "pages/discord.png"]
        }

        if self.request.POST and self.request.POST.get("agreed") != "agreed":
            context["error"] = True
        return context

    def post(self, request, *args, **kwargs):
        if self.request.POST.get("agreed") == "agreed":
            self.redirect_to = DISCORD_INVITE_URL
        return self.get(request, *args, **kwargs)


def beta_unlock(request):
    context = {"title": "Access Beta Site"}
    if request.POST.get("beta_password"):
        if request.POST["beta_password"] == PASSWORD5DOLLARS:
            request.session["CAN_USE_BETA_SITE"] = True
            return redirect("index")
        else:
            context["invalid_password"] = True
    return render(request, "museum_site/beta-unlock.html", context)


def close_tool(request):
    if request.session.get("active_tool"):
        del request.session["active_tool"]
    return redirect(request.GET.get("next", "index"))


def directory(request, category):
    """ Returns a directory of all authors/companies/genres in the database """
    data = {}
    data["category"] = category

    if category == "company":
        data_list = Company.objects.all().order_by("title")
    elif category == "author":
        data_list = Author.objects.all().order_by("title")
    elif category == "genre":
        data_list = Genre.objects.visible().order_by("title")

    data["title"] = "{} Directory".format(category.title())

    # Break the list of results into 4 columns
    data_list = sorted(data_list, key=lambda s: re.sub(r'(\W|_)', "é", s.title.lower()))

    # Split the list into 4 sets
    column_length = math.ceil(len(data_list) / 4)
    wip_columns = []
    for idx in range(0, 4):
        wip_columns.append(data_list[:column_length])
        data_list = data_list[column_length:]

    # Add headings to create final columns
    final_columns = [[], [], [], []]
    observed_letters = []
    last_letter = ""
    force_header = False
    for idx in range(0, 4):
        wip_column = wip_columns[idx]
        if idx != 0:
            force_header = True

        for entry in wip_column:
            first_letter = entry.title[0].upper()
            if first_letter in "1234567890":
                first_letter = "#"
            elif first_letter not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                first_letter = "*"
            if (first_letter not in observed_letters) or force_header:
                observed_letters.append(first_letter)
                final_columns[idx].append({"kind": "header", "title": first_letter + (" (cntd.)" if force_header else "")})
                force_header = False

            final_columns[idx].append({"url": entry.get_absolute_url(), "title": entry.title, "kind": "entry"})
        # Mark letters repeated between columns
        last_letter = first_letter

    data["columns"] = final_columns
    return render(request, "museum_site/directory.html", data)


def explicit_warning(request):
    """ Returns an in-between page asking users to confirm they wish to continue to explicit content and if they wish to disable being asked in the future """
    context = {"title": "Explicit Content Ahead!"}
    form = View_Explicit_Content_Confirmation_Form(request.POST) if request.method == "POST" else View_Explicit_Content_Confirmation_Form()

    if request.GET.get("pk"):
        context["file"] = ZFile.objects.get(pk=request.GET.get("pk"))

    if request.method == "POST":
        # Go back from explicit content
        if request.POST.get("action") == "Go Back":
            return redirect("index")

        # Process explicit warning settings
        form.process(request)

        # Continue to explicit content
        request.session["show_explicit_for"] = int(request.GET.get("pk", 0))
        return redirect(request.GET.get("next", "/"))

    context["form"] = form
    return render(request, "museum_site/explicit-warning.html", context)


def follow(request):
    context = {"title": "Follow Worlds of ZZT"}
    return render(request, "museum_site/follow.html", context)


def index(request):
    """ Returns front page """
    context = {}

    # Obtain latest content
    context["articles"] = Article.objects.spotlight()[:10]
    context["new_releases"] = ZFile.objects.new_releases_frontpage(spotlight_filter=True)[:12]
    context["files"] = ZFile.objects.new_finds(spotlight_filter=True)[:12]
    context["feedback"] = Review.objects.latest_approved_reviews().filter(spotlight=True)[:10]

    return render(request, "museum_site/index.html", context)


def mass_downloads(request):
    """ Returns a page for downloading files by release year """
    context = {"title": "Mass Downloads"}
    zzt_counts = ZFile.objects.filter(details__id=DETAIL_ZZT).annotate(year=ExtractYear("release_date")).values("year").annotate(count=Count("pk"))
    szzt_count = {"label": "Super ZZT Worlds", "count": ZFile.objects.filter(details__id=DETAIL_SZZT).count(), "zip": "szzt_worlds.zip"}
    weave_count = {"label": "Weave ZZT Worlds", "count": ZFile.objects.filter(details__id=DETAIL_WEAVE).count(), "zip": "weave_worlds.zip"}
    zig_count = {"label": "ZIG Worlds", "count": ZFile.objects.filter(details__id=DETAIL_ZIG).count(), "zip": "zig_worlds.zip"}
    utilities_count = {"label": "Utilities", "count": ZFile.objects.filter(details__id=DETAIL_UTILITY).count(), "zip": "utilities.zip"}
    zzm_audio_count = {"label": "ZZM Audio Files", "count": ZFile.objects.filter(details__id=DETAIL_ZZM).count(), "zip": "zzm_audio.zip"}
    featured_world_count = {"label": "Featured Worlds", "count": ZFile.objects.filter(details__id=DETAIL_FEATURED).count(), "zip": "featured_worlds.zip"}

    zzt_1990s = []
    zzt_2000s = []
    zzt_2010s = {"label": "ZZT Worlds - 2010-2019", "count": 0, "zip": "zzt_worlds_2010-2019.zip"}
    zzt_2020s = {"label": "ZZT Worlds - 2020-2029", "count": 0, "zip": "zzt_worlds_2020-2029.zip"}
    for item in zzt_counts:
        if item["year"] is None:
            item["year"] = "Unknown"
            item["zip"] = "zzt_worlds_UNKNOWN.zip"
            item["label"] = "ZZT Worlds - Unknown"
            zzt_1990s.append(item)
        elif int(item["year"]) < 2000:
            item["label"] = "ZZT Worlds - {}".format(item["year"])
            item["zip"] = "zzt_worlds_{}.zip".format(item["year"])
            zzt_1990s.append(item)
        elif int(item["year"]) < 2010:
            item["label"] = "ZZT Worlds - {}".format(item["year"])
            item["zip"] = "zzt_worlds_{}.zip".format(item["year"])
            zzt_2000s.append(item)
        elif int(item["year"]) < 2020:
            zzt_2010s["count"] += item["count"]
        elif int(item["year"]) < 2030:
            zzt_2020s["count"] += item["count"]

    columns = [
        zzt_1990s, zzt_2000s, [zzt_2010s, zzt_2020s], [szzt_count, weave_count, zig_count, utilities_count, zzm_audio_count, featured_world_count]
    ]

    for column in columns:
        for row in column:
            path = os.path.join(ZGAMES_BASE_PATH, "mass", row["zip"])
            if os.path.isfile(path):
                stat = os.stat(path)
                row["size"] = stat.st_size
                row["updated"] = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")

    context["columns"] = columns
    return render(request, "museum_site/mass-downloads.html", context)


def random(request):
    """ Returns a random ZZT file page """
    selection = ZFile.objects.random_zzt_world()
    if selection is not None:
        return redirect(selection.get_absolute_url())
    else:
        return redirect("index")


def set_theme(request):
    request.session["theme"] = request.GET.get("theme", "light")
    if request.GET.get("redirect"):
        return redirect("my_profile")
    else:
        return HttpResponse(request.GET.get("theme", "light"))


def site_credits(request):
    """ Returns page for site credits """
    data = {"title": "Credits"}

    # Get all article authors
    data["authors"] = Article.objects.credited_authors().distinct().values_list("author", flat=True)
    data["list"] = []
    for author in data["authors"]:
        split = author.split("/")
        for name in split:
            if name in ["Various", "None"]:
                continue
            if name not in data["list"]:
                data["list"].append(name)
    data["list"].sort(key=str.lower)
    data["split"] = math.ceil(len(data["list"]) / 4.0)

    # Hardcoded credits
    unregistered_supporters_file = os.environ.get("MOZ_UNREGISTERED_SUPPORTERS_FILE", None)
    supporters = []
    bigger_supporters = []
    biggest_supporters = []
    hc_emails = []
    bigger_hc_emails = []
    biggest_hc_emails = []

    if unregistered_supporters_file is not None:
        with open(unregistered_supporters_file) as fh:
            raw = json.loads(fh.read())

        for row in raw:
            if row.get("pledge") == "biggest":
                biggest_supporters.append(row)
            elif row.get("pledge") == "bigger":
                bigger_supporters.append(row)
            else:
                supporters.append(row)

        # Emails to reference
        for row in supporters:
            hc_emails.append(row["email"])
        for row in bigger_supporters:
            bigger_hc_emails.append(row["email"])
        for row in biggest_supporters:
            biggest_hc_emails.append(row["email"])
    else:
        supporters = []
        bigger_supporters = []
        biggest_supporters = []

    # Get users known to be patrons
    no_longer_hardcoded = []
    patrons = Profile.objects.patrons()
    for p in patrons:
        if p.site_credits_name:
            info = {"name": p.site_credits_name, "char": p.char, "fg": p.fg, "bg": p.bg, "img": "blank-portrait.png", "email": p.patron_email}

            if p.patron_email in hc_emails:
                idx = hc_emails.index(p.patron_email)
                hc_emails[idx] = info
                no_longer_hardcoded.append(p.patron_email)
                continue
            elif p.patron_email in bigger_hc_emails:
                idx = bigger_hc_emails.index(p.patron_email)
                bigger_hc_emails[idx] = info
                no_longer_hardcoded.append(p.patron_email)
                continue
            elif p.patron_email in biggest_hc_emails:
                idx = biggest_hc_emails.index(p.patron_email)
                biggest_hc_emails[idx] = info
                no_longer_hardcoded.append(p.patron_email)
                continue

            if p.patronage >= 10000:
                biggest_supporters.append(info)
            elif p.patronage >= 2000:
                bigger_supporters.append(info)
            else:
                supporters.append(info)

    supporters.sort(key=lambda k: k["name"].lower())
    bigger_supporters.sort(key=lambda k: k["name"].lower())
    biggest_supporters.sort(key=lambda k: k["name"].lower())

    # Pad out entries to look cleaner
    while len(bigger_supporters) % 3 != 0:
        bigger_supporters.append({"name": "ZZZZZZZZZZSTUB", "email": "STUB"})
    while len(biggest_supporters) % 2 != 0:
        biggest_supporters.append({"name": "ZZZZZZZZZZSTUB", "email": "STUB"})
    while len(supporters) % 3 != 0:
        supporters.append({"name": "ZZZZZZZZZZSTUB", "email": "STUB"})

    data["supporters"] = supporters
    data["bigger_supporters"] = bigger_supporters
    data["biggest_supporters"] = biggest_supporters

    return render(request, "museum_site/site-credits.html", data)


def stub(request, *args, **kwargs):
    data = {"title": "STUB VIEW"}
    return render(request, "museum_site/index.html", data)


def worlds_of_zzt_queue(request):
    context = {"title": "Worlds of ZZT Queue"}
    category = request.GET.get("category", "wozzt")

    if request.user.is_staff:
        if request.method == "POST":
            if request.POST.get("action") == "roll":
                context["wozzt_roll_form"] = WoZZT_Roll_Form(request.POST)
                if context["wozzt_roll_form"].is_valid():
                    context["wozzt_roll_form"].process()

        else:
            context["wozzt_roll_form"] = WoZZT_Roll_Form(initial={"category": category})

        if request.POST.get("action"):
            if request.POST["action"] == "set-priority":
                pk = int(request.POST.get("id"))
                entry = WoZZT_Queue.objects.get(pk=pk)
                entry.priority = int(request.POST.get("priority"))
                entry.save()
                return HttpResponse("OK")
            elif request.POST["action"] == "delete":
                pk = int(request.POST.get("id"))
                entry = WoZZT_Queue.objects.get(pk=pk)
                entry.delete_image()
                entry.delete()
                return HttpResponse("OK")
    else:
        if category not in ["wozzt", "tuesday"]:  # Guest can only view main queue and title screen tuesday queue
            category = "wozzt"

    context["queue"] = WoZZT_Queue.objects.queue_for_category(category)
    context["queue_size"] = len(context["queue"])
    size = 999 if (request.user.is_authenticated and request.user.profile.patron) or request.user.is_staff else 16
    context["queue"] = context["queue"][:size]
    context["category"] = category
    return render(request, "museum_site/wozzt-queue.html", context)


def error_500(request):
    # Attempt to redirect old URLs with .zip
    components = request.path.split("/")
    new_components = []
    attempt_redirect = False

    for c in components:
        if c.lower().endswith(".zip"):
            attempt_redirect = True
            c = c[:-4]
        new_components.append(c)

    if attempt_redirect:
        new_path = "/".join(new_components)
        return redirect(new_path)

    return HttpResponse("500 Error - Museum of ZZT", status=500)


def error_403(request, exception=None):
    return render(request, "museum_site/403.html", {}, status=403)


def error_404(request, exception=None):
    return render(request, "museum_site/404.html", {}, status=404)


class Policy_View(TemplateView):
    def get_template_names(self):
        return "museum_site/policy-{}.html".format(self.kwargs["slug"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.kwargs["slug"].replace("-", " ").title() + " Policy"
        return context


class RSS_View(TemplateView):
    template_name = "museum_site/rss-info.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "RSS Feeds"
        return context


class Company_Overview_View(DetailView):
    template_name = "museum_site/company-view.html"
    context_object_name = "company"

    def get_queryset(self):
        return Company.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = context["company"].title
        context["releases"] = ZFile.objects.filter(companies=context["company"].pk)
        return context

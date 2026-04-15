import json
import math
import os

from datetime import datetime, UTC

from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.db.models import Count
from django.db.models.functions import ExtractYear
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.defaultfilters import slugify, timeuntil
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.urls import reverse

from museum_site.core.detail_identifiers import *
from museum_site.core.misc import get_ascii_table_data, get_color_table_data, get_frontpage_events, get_patron_supporters, list_to_columns, Meta_Tag_Block
from museum_site.constants import ZGAMES_BASE_PATH
from museum_site.forms.zfile_forms import View_Explicit_Content_Confirmation_Form
from museum_site.forms.wozzt_forms import WoZZT_Roll_Form
from museum_site.models import Article, Author, Company, File, Genre, Profile, Review, WoZZT_Queue
from museum_site.models import File as ZFile
from museum_site.settings import DISCORD_INVITE_URL, PASSWORD5DOLLARS
from stream.models import Stream


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
        if hasattr(self, "redirect_to") and self.redirect_to is not None:
            return redirect(self.redirect_to)
        return super().render_to_response(context, **response_kwargs)


class Ascii_Reference_View(Museum_Base_Template_View):
    title = "Ascii Character Reference"
    template_name = "museum_site/ascii-reference.html"
    preview_image = "pages/ascii-reference.png"
    description = "A reference page for the ASCII characters used by ZZT"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meta_tags"] = Meta_Tag_Block(url=self.request.get_full_path(), title=self.title, image=self.preview_image, description=self.description)
        context["range"] = list(range(0, 256))
        context["scale"] = 2
        context["orientation"] = "horiz"
        context["ascii_table"] = get_ascii_table_data()
        (context["palette_lo"], context["palette_hi"]) = get_color_table_data()
        return context


class Audio_Player_View(Museum_Base_Template_View):
    title = "Audio Player"
    template_name = "museum_site/audio-player.html"
    preview_image = "pages/audio-player.png"
    description = "Listen to transcriptions of ZZT audio and create your own compositions."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meta_tags"] = Meta_Tag_Block(url=self.request.get_full_path(), title=self.title, image=self.preview_image, description=self.description)
        return context


class Discord_Overview_View(Museum_Base_Template_View):
    title = "Joining The Worlds of ZZT Discord"
    template_name = "museum_site/discord.html"
    description = "Rules, information, and an invite link to the Worlds of ZZT Discord server"
    preview_image = "pages/discord.png"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST and self.request.POST.get("agreed") != "agreed":
            context["error"] = True

        context["meta_tags"] = Meta_Tag_Block(url=self.request.get_full_path(), title=self.title, image=self.preview_image, description=self.description)
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
    context = {}
    context["category"] = category
    cat_descs = {"company": "companies known to the Museum of ZZT", "author": "authors known to the Museum of ZZT", "genre": "genres available on the Museum of ZZT", "year": "years"}

    if category == "company":
        data_list = Company.objects.all().order_by("title")
    elif category == "author":
        data_list = Author.objects.all().order_by("title")
    elif category == "genre":
        data_list = Genre.objects.visible().order_by("title")
    elif category == "year":
        data_list = list(range(datetime.now(UTC).year, 1990, -1))
        data_list.append("unk")

    context["columns"] = list_to_columns(category, data_list)
    context["title"] = "{} Directory".format(category.title())
    context["meta_tags"] = Meta_Tag_Block(url=request.get_full_path(), title=context["title"], description="Directory of all {}".format(cat_descs.get(category)))
    return render(request, "museum_site/directory.html", context)


def explicit_warning(request):
    """ Returns an in-between page asking users to confirm they wish to continue to explicit content and if they wish to disable being asked in the future """
    context = {"title": "Explicit Content Ahead!", "file": None}
    form = View_Explicit_Content_Confirmation_Form(request.POST) if request.method == "POST" else View_Explicit_Content_Confirmation_Form()
    context["file"] = get_object_or_404(ZFile, pk=request.GET.get("pk"))

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
    context["meta_tags"] = Meta_Tag_Block(url=request.get_full_path(), title=context["title"], author=", ".join(context["file"].related_list("authors")), image=context["file"].preview_url(), description="Explicit content warning for {}".format(context["file"].title))
    return render(request, "museum_site/explicit-warning.html", context)


def follow(request):
    context = {"title": "Follow Worlds of ZZT"}
    context["meta_tags"] = Meta_Tag_Block(url=request.get_full_path(), title=context["title"], description="Links to every social media and other external site with a Worlds of ZZT account you can follow including Bluesky, Mastodon, Twitch, RSS feeds, Patreon, and more")
    return render(request, "museum_site/follow.html", context)


def index(request):
    """ Returns front page """
    context = {}

    context["main_event"] = get_frontpage_events(qs=Stream.objects)

    # Obtain latest content
    context["articles"] = Article.objects.spotlight()[:10]
    context["new_releases"] = ZFile.objects.new_releases_frontpage(spotlight_filter=True)[:12]
    context["files"] = ZFile.objects.new_finds(spotlight_filter=True)[:12]
    context["feedback"] = Review.objects.latest_approved_reviews().filter(spotlight=True)[:10]
    context["meta_tags"] = Meta_Tag_Block(url=request.get_full_path(), image="pages/og_default.png", description="The Museum of ZZT is an online archive dedicated to the preservation and curation of ZZT worlds. Explore more than 4000 indie-made ZZT worlds spanning its 35+ year history")
    return render(request, "museum_site/index.html", context)


def mass_downloads(request):
    """ Returns a page for downloading files by release year """
    context = {"title": "Mass Downloads"}
    context["mass_dl_info"] = []

    cached_data = json.loads(cache.get("MOZ_MASS_DL_INFO", "{}"))
    for k, v in cached_data.items():
        entry = {"key": v["year"], "count": v["count"], "generated": v["generated"], "zip_name": v["zip_name"], "title": v["title"], "size": v["size"]}
        if k in ["UNKNOWN", "2000", "2010-2019", "szzt_worlds"]:
            entry["start_table"] = True
        context["mass_dl_info"].append(entry)

    context["meta_tags"] = Meta_Tag_Block(url=request.get_full_path(), title=context["title"], description="Mass downloads of all files hosted on the Museum of ZZT grouped by year and category. Quickly obtain a complete archive of ZZT worlds!")
    return render(request, "museum_site/mass-downloads.html", context)


def random(request):
    """ Returns a random ZZT file page """
    selection = ZFile.objects.random_zzt_world()
    url = selection.get_absolute_url() if selection is not None else "index"
    return redirect(url + "?rnd=1")


def set_setting(request):
    param = request.GET.get("setting")
    if param is None:
        return redirect("index")

    key, value = param.split("|")
    # First valid setting is treated as default
    USER_SETTING_CHOICES = {
        "sidebars": ["show", "hide"],
        "theme": ["light", "dark"],
        "prezoom": ["off", "on"],
        "TEMP_FILE_VIEWER_BETA": ["v1", "v2"],
        "view": ["detailed", "list", "gallery"],
        "DEBUG": ["off", "on"],
        "zzt32_exe": ["zzt", "czoo", "solidhud"],
        "zfile_descriptions": ["show", "hide"],
        "explicit_content_warnings": ["show", "hide"],
    }

    if key in USER_SETTING_CHOICES.keys():
        request.session[key] = value if value in USER_SETTING_CHOICES[key] else USER_SETTING_CHOICES[key][0]
        if value == USER_SETTING_CHOICES[key][0]:  # Don't bother storing defaults
            del request.session[key]
            output = {"key": key, "value": value}
        else:
            output = {"key": key, "value": request.session[key]}
    else:
        return redirect("index")

    if request.GET.get("redirect"):
        return redirect(request.GET["redirect"])
    else:
        return JsonResponse(output)


def site_credits(request):
    """ Returns page for site credits """
    context = {"title": "Credits"}

    # Get all article authors
    context["authors"] = ["Dr. Dos"] + list(set(Article.objects.credited_authors().exclude(author="Dr. Dos").values_list("author", flat=True).distinct()))
    context["list"] = []
    for author in context["authors"]:
        split = author.split("/")
        for name in split:
            if name in ["Various", "None"]:
                continue
            if name not in context["list"]:
                context["list"].append(name)
    context["list"].sort(key=str.lower)
    context["split"] = math.ceil(len(context["list"]) / 4.0)

    (supporters, bigger_supporters, biggest_supporters) = get_patron_supporters(patrons=Profile.objects.patrons())

    context["supporters"] = supporters
    context["bigger_supporters"] = bigger_supporters
    context["biggest_supporters"] = biggest_supporters
    context["meta_tags"] = Meta_Tag_Block(url=request.get_full_path(), title=context["title"], description="Museum of ZZT Site Credits")
    return render(request, "museum_site/site-credits.html", context)


def strawpoll(request):
    redir = cache.get("STRAWPOLL_STREAM_VOTE")
    if redir:
        return redirect(redir)
    context = {"title": "No Stream Poll Available"}
    return render(request, "museum_site/strawpoll-unavailable.html", context)


def stub(request, *args, **kwargs):
    context = {"title": "STUB VIEW"}
    return render(request, "museum_site/index.html", context)


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
    context["meta_tags"] = Meta_Tag_Block(url=request.get_full_path(), title=context["title"], image="pages/worlds-of-zzt.png", description="Upcoming posts of randomly selected ZZT boards to be posted to the Worlds of ZZT bot feed.")
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
        context["meta_tags"] = Meta_Tag_Block(url=self.request.get_full_path(), title=context["title"])
        return context


class RSS_View(TemplateView):
    template_name = "museum_site/rss-info.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "RSS Feeds"
        context["meta_tags"] = Meta_Tag_Block(url=self.request.get_full_path(), title=context["title"], description="RSS feeds available from the Museum of ZZT. Keep up to date on new articles, reviews, and uploaded files!")
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


@staff_member_required
def add_zfile_assocs(request):
    a = Article.objects.get(pk=request.GET.get("article_pk"))
    # Find ZFile PKs to add file associations
    for line in a.content[:2048].split("\n"):
        if line.find("|get_files_by_id") != -1:
            start = line.find('"') + 1
            end = line.find('"|')
            pk_str = line[start:end]
            pks = pk_str.split(",")
            for pk in pks:
                zf = File.objects.filter(pk=int(pk)).first()
                if zf:
                    zf.articles.add(a)
                    zf.save()
    return redirect(request.GET.get("path", "/"))

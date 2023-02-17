import json
import math
import re

from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render

from museum_site.common import *
from museum_site.constants import *
from museum_site.models import *
from museum_site.private import (
    UNREGISTERED_SUPPORTERS, UNREGISTERED_BIGGER_SUPPORTERS,
    UNREGISTERED_BIGGEST_SUPPORTERS, DISCORD_INVITE_URL
)


def ascii_reference(request):
    context = {"title": "Ascii Character Reference"}
    context["range"] = list(range(0, 256))
    context["scale"] = 2
    context["orientation"] = "horiz"
    context["meta_context"] = {
        "description": ["name", "A reference page for the ASCII characters used by ZZT"],
        "og:title": ["property", context["title"] + " - Museum of ZZT"],
        "og:image": ["property", "pages/ascii-reference.png"]
    }
    return render(request, "museum_site/ascii-reference.html", context)


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
    first_letters = []

    for entry in data_list:
        if entry.title == "":
            continue
        elif entry.title[0] in "1234567890":
            first_letters.append("#")
        elif entry.title[0].upper() not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            first_letters.append("*")
        else:
            first_letters.append(entry.title[0].upper())

    data["list"] = list(zip(data_list, first_letters))
    data["split"] = math.ceil(len(data_list) / 4.0)

    return render(request, "museum_site/directory.html", data)


def explicit_warning(request):
    data = {}
    data["title"] = "Explicit Content Ahead!"

    if request.POST.get("action") == "Continue":
        if request.POST.get("explicit-warning") == "off":
            request.session["bypass_explicit_content_warnings"] = True
        else:
            if request.session.get("bypass_explicit_content_warnings"):
                del request.session["bypass_explicit_content_warnings"]
            request.session["show_explicit_for"] = int(request.GET.get("pk", 0))

        next_page = request.GET.get("next")
        if next_page.startswith("/"):
            next_page = next_page[1:]
        return redirect(HOST + next_page)
    elif request.POST.get("action") == "Go Back":
        return redirect("index")

    return render(request, "museum_site/explicit-warning.html", data)


def discord_overview(request):
    context = {"title": "Joinining The Worlds of ZZT Discord"}
    context["meta_context"] = {
        "description": ["name", "Rules, information, and an invite link to the Worlds of ZZT Discord server"],
        "og:title": ["property", context["title"] + " - Museum of ZZT"],
        "og:image": ["property", "pages/discord.png"]
    }

    if request.method == "POST":
        if request.POST.get("agreed") != "agreed":
            context["error"] = True
        return redirect(DISCORD_INVITE_URL)

    return render(request, "museum_site/discord.html", context)


def generic_template_page(request, title="", template="", context={}):
    context["title"] = title
    return render(request, template, context)


def index(request):
    """ Returns front page """
    data = {}

    # Obtain latest content
    data["articles"] = Article.objects.spotlight()[:FP.ARTICLES_SHOWN]
    data["new_releases"] = File.objects.new_releases_frontpage(spotlight_filter=True)[:FP.NEW_RELEASES_SHOWN]
    data["files"] = File.objects.new_finds(spotlight_filter=True)[:FP.FILES_SHOWN]
    data["reviews"] = Review.objects.latest_approved_reviews()[:FP.REVIEWS_SHOWN]
    data["article_table_header"] = data["articles"][0].table_header() if data["articles"] else None
    data["review_table_header"] = data["reviews"][0].table_header() if data["reviews"] else None

    return render(request, "museum_site/index.html", data)


def mass_downloads(request):
    """ Returns a page for downloading files by release year """
    data = {"title": "Mass Downloads"}

    # Counts for each year
    """
    data["counts"] = {}
    dates = File.objects.all().only("release_date")
    for row in dates:
        year = str(row.release_date)[:4]
        if year not in data["counts"].keys():
            data["counts"][year] = 1
        else:
            data["counts"][year] += 1
    """

    return render(request, "museum_site/mass_downloads.html", data)


def random(request):
    """ Returns a random ZZT file page """
    selection = File.objects.random_zzt_world()
    if selection is not None:
        return redirect(selection.view_url())
    else:
        return redirect("index")


def set_theme(request):
    request.session["theme"] = request.GET.get("theme", "light")
    if request.GET.get("redirect"):
        return redirect("my_profile")
    else:
        return HttpResponse(request.GET.get("theme", "light"))


def scroll_navigation(request):

    if request.GET.get("id"):
        ref = int(request.GET["id"])
        scroll = None
        if "next" in request.path:
            scroll = Scroll.objects.filter(published=True, identifier__gt=ref).order_by("id").first()
        elif "prev" in request.path:
            scroll = Scroll.objects.filter(published=True, identifier__lt=ref).order_by("-id").first()
        identifier = scroll.identifier if scroll else 1
    else:
        if "first" in request.path:
            scroll = Scroll.objects.filter(published=True).order_by("id").first()
        elif "latest" in request.path:
            scroll = Scroll.objects.filter(published=True).order_by("-id").first()
        else:  # Random
            scroll = Scroll.objects.filter(published=True).order_by("?").first()
        identifier = scroll.identifier if scroll else 1
    return redirect("/scroll/view/{}/".format(identifier))


def site_credits(request):
    """ Returns page for site credits """
    data = {"title": "Credits"}

    # Get all article authors
    data["authors"] = Article.objects.credited_authors().distinct().values_list(
        "author", flat=True
    )
    data["list"] = []
    for author in data["authors"]:
        split = author.split("/")
        for name in split:
            if name != "Various" and name not in data["list"]:
                data["list"].append(name)
    data["list"].sort(key=str.lower)
    data["split"] = math.ceil(len(data["list"]) / 4.0)

    # Hardcoded credits
    supporters = UNREGISTERED_SUPPORTERS
    bigger_supporters = UNREGISTERED_BIGGER_SUPPORTERS
    biggest_supporters = UNREGISTERED_BIGGEST_SUPPORTERS

    # Emails to reference
    hc_emails = []
    bigger_hc_emails = []
    biggest_hc_emails = []
    for row in supporters:
        hc_emails.append(row["email"])
    for row in bigger_supporters:
        bigger_hc_emails.append(row["email"])
    for row in biggest_supporters:
        biggest_hc_emails.append(row["email"])

    # Get users known to be patrons
    no_longer_hardcoded = []
    patrons = Profile.objects.patrons()
    for p in patrons:
        if p.site_credits_name:
            info = {
                "name": p.site_credits_name,
                "char": p.char,
                "fg": p.fg,
                "bg": p.bg,
                "img": "blank-portrait.png",
                "email": p.patron_email
            }

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
    data = {"title": "Worlds of ZZT Queue"}
    category = request.GET.get("category", "wozzt")

    if request.user.is_staff:
        if request.POST.get("action"):
            if request.POST["action"] == "roll":
                count = request.POST.get("count")
                category = request.POST.get("category")
                title = True if category == "tuesday" else False

                for x in range(0, int(count)):
                    WoZZT_Queue().roll(category=category, title_screen=title)

            elif request.POST["action"] == "set-priority":
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

    data["queue"] = WoZZT_Queue.objects.queue_for_category(category)
    data["queue_size"] = len(data["queue"])

    size = 16
    if (request.user.is_authenticated and request.user.profile.patron) or request.user.is_staff or category == "farewell":
        size = 999
    data["queue"] = data["queue"][:size]
    return render(request, "museum_site/wozzt-queue.html", data)


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

    return HttpResponse("500 Error")


def error_403(request, exception=None):
    context = {}
    return render(request, "museum_site/403.html", context)


def error_404(request, exception=None):
    context = {}
    return render(request, "museum_site/404.html", context)

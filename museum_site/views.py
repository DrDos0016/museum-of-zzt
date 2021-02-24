from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from .common import *
from .constants import *
from .models import *


def directory(request, category):
    """ Returns a directory of all authors/companies/genres in the database """
    data = {}
    data["category"] = category

    """ This can possibly be cached in some way, it's not going to change
    often.
    """
    data_list = []
    if category == "company":
        data["title"] = "Companies"
        companies = File.objects.values(
            "company"
        ).exclude(
            company=None
        ).exclude(
            company=""
        ).distinct().order_by("company")
        for c in companies:
            split = c["company"].split("/")
            for credited in split:
                if credited not in data_list:
                    data_list.append(credited)
    elif category == "author":
        data["title"] = "Authors"
        authors = File.objects.values("author").distinct().order_by("author")
        for a in authors:
            split = a["author"].split("/")
            for credited in split:
                if credited not in data_list:
                    data_list.append(credited)
    elif category == "genre":
        data["title"] = "Genres"
        data_list = GENRE_LIST

    # Break the list of results into 4 columns
    data_list = sorted(data_list, key=lambda s: re.sub(r'(\W|_)', "é", s.lower()))
    # data_list = sorted(data_list, key=lambda s: s.lower())
    first_letters = []

    for entry in data_list:
        if entry[0] in "1234567890":
            first_letters.append("#")
        elif entry[0].upper() not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            first_letters.append("*")
        else:
            first_letters.append(entry[0].upper())

    data["list"] = list(zip(data_list, first_letters))
    data["split"] = math.ceil(len(data_list) / 4.0)
    return render(request, "museum_site/directory.html", data)


def exhibit(request, letter, filename, section=None, local=False):
    """ Returns page exploring a file's zip contents """
    data = {}
    data["custom_layout"] = "fv-grid"
    data["year"] = YEAR
    data["details"] = []  # Required to show all download links
    data["file"] = File.objects.get(letter=letter, filename=filename)
    data["local"] = local
    if not local:
        data["title"] = data["file"].title
        data["letter"] = letter

        # Check for recommended custom charset
        if data["file"].id in list(CUSTOM_CHARSET_MAP.keys()):
            data["custom_charset"] = CUSTOM_CHARSET_MAP[data["file"].id]

        if data["file"].is_uploaded():
            letter = "uploaded"
            data["uploaded"] = True

        data["files"] = []

        if ".zip" in filename.lower():
            zip_file = zipfile.ZipFile(os.path.join(SITE_ROOT, "zgames", letter, filename))
            files = zip_file.namelist()
            files.sort(key=str.lower)
            data["zip_info"] = zip_file.infolist()

            # Filter out directories (but not their contents)
            for f in files:
                if f and f[-1] != os.sep:
                    data["files"].append(f)
            data["load_file"] = urllib.parse.unquote(request.GET.get("file", ""))
            data["load_board"] = request.GET.get("board", "")
    else:  # Local files
        data["file"] = "Local File Viewer"
        data["letter"] = letter

    data["charsets"] = CHARSET_LIST
    data["custom_charsets"] = CUSTOM_CHARSET_LIST

    return render(request, "museum_site/exhibit.html", data)


def generic(request, title="", template=""):
    data = {"title": title}
    return render(request, "museum_site/" + template + ".html")


def index(request):
    """ Returns front page """
    data = {}

    # Obtain latest content
    data["articles"] = Article.objects.filter(published=PUBLISHED_ARTICLE, spotlight=True).order_by("-date")[:FP_ARTICLES_SHOWN]
    data["files"] = File.objects.filter(spotlight=True).exclude(details__id__in=[DETAIL_UPLOADED]).order_by("-publish_date", "-id")[:FP_FILES_SHOWN]
    data["reviews"] = Review.objects.all().order_by("-date")[:FP_REVIEWS_SHOWN]

    # Calculate upload queue size
    request.session["FILES_IN_QUEUE"] = File.objects.filter(details__id__in=[DETAIL_UPLOADED]).count()

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
    print(data["counts"])
    """


    return render(request, "museum_site/mass_downloads.html", data)


def play_collection(request):
    """ Returns page to play file in the browser """
    data = {}
    data["title"] = " - Play Collection"
    data["player"] = "zeta"  # Must be Zeta
    data["custom_charset"] = None  # Modified graphics aren't really viable here
    data["engine"] = "zzt.zip"  # TODO: Special case for SZZT
    data["play_base"] = "museum_site/world.html"

    if request.GET.get("letter"):
        data["letter"] = request.GET.get("letter")

    if request.GET.get("popout"):
        data["play_base"] = "museum_site/play-popout.html"

    # Get the files in the collection
    if request.GET.get("mode") == "featured":
        files = File.objects.filter(details__id__in=[DETAIL_FEATURED])
    elif request.GET.get("mode") == "new":
        files = File.objects.all().order_by(*SORT_CODES["published"])
    elif request.GET.get("mode") == "browse":
        files = File.objects.filter(letter=data["letter"])

    # TODO: WEIRDLY BROKEN TITLES
    files = files.exclude(pk=431)  # 4 by Jojoisjo
    files = files.exclude(pk=85)  # Banana Quest

    # Slice by page

    data["page"] = int(request.GET.get("page", 1))
    data["files"] = files[
        (data["page"] - 1) * PAGE_SIZE:data["page"] * PAGE_SIZE
    ]

    data["file"] = None
    data["extra_files"] = ""
    for f in data["files"][1:]:
        if f.file_exists():
            if data["file"] is None:
                data["file"] = f
            else:
                data["extra_files"] += '"{}",\n'.format(f.download_url())

    response = render(request, "museum_site/play_collection.html", data)
    return response


def random(request):
    """ Returns a random ZZT file page """
    max_pk = File.objects.all().order_by("-id")[0].id

    zgame = None
    while not zgame:
        pk = randint(1, max_pk)
        zgames = File.objects.filter(pk=pk, details__id=DETAIL_ZZT).exclude(
            details__id__in=[DETAIL_LOST, DETAIL_REMOVED]
        ).exclude(genre__icontains="Explicit")
        if zgames:
            zgame = zgames[0]

    return redirect(zgame.file_url())


def redir(request, url):
    return redirect(url, permanent=True)


def site_credits(request):
    """ Returns page for site credits """
    data = {"title": "Credits"}

    # Get all article authors
    data["authors"] = Article.objects.exclude(author="N/A").distinct().values_list("author", flat=True)
    data["list"] = []
    for author in data["authors"]:
        split = author.split("/")
        for name in split:
            if name not in data["list"]:
                data["list"].append(name)
    data["list"].sort(key=str.lower)
    data["split"] = math.ceil(len(data["list"]) / 4.0)
    return render(request, "museum_site/credits.html", data)


@staff_member_required
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

            elif request.POST["action"] == "delete":
                pk = int(request.POST.get("id"))
                entry = WoZZT_Queue.objects.get(pk=pk)
                entry.delete_image()
                entry.delete()

    data["queue"] = WoZZT_Queue.objects.filter(category=category).order_by("-priority", "id")
    data["queue_size"] = len(data["queue"])
    return render(request, "museum_site/wozzt-queue.html", data)

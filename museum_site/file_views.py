from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from .common import *
from .constants import *
from .models import *
from .private import BANNED_IPS


def file_directory(
    request,
    letter=None,
    details=[DETAIL_ZZT, DETAIL_SZZT, DETAIL_UTILITY],
    page_num=1,
    show_description=False
):
    """ Returns page listing all articles sorted either by date or name """
    data = {"title": "Browse"}

    data["sort_options"] = [
        {"text": "Title", "val": "title"},
        {"text": "Author", "val": "author"},
        {"text": "Company", "val": "company"},
        {"text": "Rating", "val": "rating"},
        {"text": "Release Date", "val": "release"},
    ]

    default_sort = None

    # Pull files based on page
    qs = File.search(request.GET)
    if details:
        qs = qs.filter(details__in=details)
        if len(details) == 1:
            data["title"] = "Browse - " + CATEGORY_LIST[details[0]][1]
            data["header"] = data["title"]
    if letter:
        qs = qs.filter(letter=letter)
        data["title"] = "Browse - " + letter.upper()
        data["header"] = data["title"]
    if request.path == "/new":
        data["title"] = "New Additions"
        data["header"] = data["title"]
    elif request.path == "/uploaded":
        data["title"] = "Upload Queue"
        data["header"] = data["title"]
        # Calculate upload queue size
        request.session["FILES_IN_QUEUE"] = File.objects.filter(
            details__id__in=[DETAIL_UPLOADED]
        ).count()
        # Add sort by upload date
        data["sort_options"] = (
            [{"text": "Upload Date", "val": "uploaded"}] + data["sort_options"]
        )
        default_sort = "-upload_date"

    if request.GET.get("sort") == "title":
        qs = qs.order_by("sort_title")
    elif request.GET.get("sort") == "author":
        qs = qs.order_by("author")
    elif request.GET.get("sort") == "company":
        qs = qs.order_by("company")
    elif request.GET.get("sort") == "rating":
        qs = qs.order_by("-rating")
    elif request.GET.get("sort") == "release":
        qs = qs.order_by("-release_date")
    elif request.GET.get("sort") == "uploaded":
        qs = qs.order_by("-upload_date")
    elif default_sort:
        qs = qs.order_by(default_sort)

    data["available_views"] = ["detailed", "list", "gallery"]
    data["view"] = get_selected_view_format(request, data["available_views"])

    page_number = int(request.GET.get("page", 1))
    page_size = get_page_size(data["view"])
    start = (page_number - 1) * page_size
    data["paginator"] = Paginator(qs, page_size)
    if page_number > data["paginator"].num_pages:
        page_number = 1
    data["page"] = data["paginator"].get_page(page_number)
    data["page_number"] = page_number

    data["guide_words"] = True
    data["first_item"] = data["page"].object_list[0]
    data["last_item"] = data["page"].object_list[PAGE_SIZE - 1]

    # Show description for certain views
    if DETAIL_LOST in details:
        data["show_description"] = True

    return render(request, "museum_site/file_directory.html", data)


def file_articles(request, letter, filename):
    """ Returns page listing all articles associated with a provided file. """
    data = {}
    data["file"] = File.objects.get(letter=letter, filename=filename)
    data["title"] = data["file"].title + " - Articles"
    data["articles"] = data["file"].articles.all()
    data["letter"] = letter

    return render(request, "museum_site/article.html", data)


def file_viewer(request, letter, filename, local=False):
    """ Returns page exploring a file's zip contents """
    data = {}
    data["custom_layout"] = "fv-grid"
    data["year"] = YEAR
    data["details"] = []  # Required to show all download links
    data["local"] = local
    if not local:
        data["file"] = File.objects.get(letter=letter, filename=filename)
        data["title"] = data["file"].title
        data["letter"] = letter

        # Check for recommended custom charset
        for charset in CUSTOM_CHARSETS:
            if data["file"].id == charset["id"]:
                data["custom_charset"] = charset["filename"]
                break

        if data["file"].is_uploaded():
            letter = "uploaded"
            data["uploaded"] = True

        data["files"] = []

        if ".zip" in filename.lower():
            zip_file = zipfile.ZipFile(
                os.path.join(SITE_ROOT, "zgames", letter, filename)
            )
            files = zip_file.namelist()
            files.sort(key=str.lower)
            data["zip_info"] = sorted(
                zip_file.infolist(), key=lambda k: k.filename.lower()
            )

            # Filter out directories (but not their contents)
            for f in files:
                if (
                    f and f[-1] != os.sep
                    and not f.startswith("__MACOSX" + os.sep)
                    and not f.upper().endswith(".DS_STORE")
                ):
                    data["files"].append(f)
            data["load_file"] = urllib.parse.unquote(
                request.GET.get("file", "")
            )
            data["load_board"] = request.GET.get("board", "")
    else:  # Local files
        data["file"] = "Local File Viewer"
        data["letter"] = letter

    data["charsets"] = []
    data["custom_charsets"] = []

    if not data["local"]:
        if data["file"].is_zzt():
            for charset in CHARSETS:
                if charset["engine"] == "ZZT":
                    data["charsets"].append(charset)
            for charset in CUSTOM_CHARSETS:
                if charset["engine"] == "ZZT":
                    data["custom_charsets"].append(charset)
        elif data["file"].is_super_zzt():
            for charset in CHARSETS:
                if charset["engine"] == "SZZT":
                    data["charsets"].append(charset)
            for charset in CUSTOM_CHARSETS:
                if charset["engine"] == "SZZT":
                    data["custom_charsets"].append(charset)
        elif data["file"].is_uploaded():
            data["charsets"] = CHARSETS
            data["custom_charsets"] = CUSTOM_CHARSETS
    # TODO LOCAL FILES CAN'T GET CHARSETS WITH THIS
    else:
        data["charsets"] = CHARSETS
        data["custom_charsets"] = CUSTOM_CHARSETS

    return render(request, "museum_site/file.html", data)


def review(request, letter, filename):
    """ Returns a page of reviews for a file. Handles POSTing new reviews """
    data = {}
    data["file"] = File.objects.get(letter=letter, filename=filename)
    data["letter"] = letter
    data["title"] = data["file"].title + " - Reviews"

    # POST review
    if request.POST.get("action") == "post-review" and data["file"].can_review:
        if request.META["REMOTE_ADDR"] in BANNED_IPS:
            return HttpResponse("Banned account.")

        review = Review()
        created = review.from_request(request)
        if created:
            review.full_clean()
            review.save()

        # Update file's review count/scores
        data["file"].calculate_reviews()
        data["file"].save()

    data["reviews"] = Review.objects.filter(file_id=data["file"].id)
    return render(request, "museum_site/review.html", data)


def roulette(
    request,
    letter=None,
    details=[DETAIL_ZZT, DETAIL_SZZT, DETAIL_UTILITY],
    page_num=1,
    show_description=False
):
    data = {"title": "Browse", "mode": "Roulette", "header": "Roulette"}

    ids = list(
        File.objects.filter(
            details__id__in=details
        ).values_list("id", flat=True)
    )
    data["rng_seed"] = str(int(request.GET.get("seed", time())))
    seed(data["rng_seed"])
    shuffle(ids)
    qs = File.objects.filter(id__in=ids[:PAGE_SIZE]).order_by("?")

    data["available_views"] = ["detailed"]
    data["view"] = get_selected_view_format(request, data["available_views"])

    data["paginator"] = Paginator(qs, PAGE_SIZE)
    data["page"] = data["paginator"].get_page(1)

    return render(request, "museum_site/file_directory.html", data)
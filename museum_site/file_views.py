from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .common import *
from .constants import *
from .forms import ReviewForm
from .models import *


def file_attributes(request, letter, filename):
    data = {}
    data["file"] = get_object_or_404(File, letter=letter, filename=filename)
    data["upload_info"] = Upload.objects.filter(file_id=data["file"]).first()
    data["reviews"] = Review.objects.filter(
        zfile__id=data["file"].pk
    ).defer("content")
    data["title"] = data["file"].title + " - Attributes"

    return render(request, "museum_site/attributes.html", data)


def files_by_detail(request, slug):
    d = get_object_or_404(Detail, slug=slug)
    return file_directory(request, details=[d.pk])


def file_directory(
    request,
    letter=None,
    details=[DETAIL_ZZT, DETAIL_SZZT, DETAIL_UTILITY],
    page_num=1,
    show_description=False,
    show_featured=False
):
    """ Returns page listing all articles sorted either by date or name """
    data = {
        "title": "Browse",
        "show_description": show_description,
        "show_featured": show_featured,
        "model": "File",
        "sort": request.GET.get("sort"),
        "table_header": table_header(File.table_fields),
        "available_views": File.supported_views,
        "view": get_selected_view_format(request, File.supported_views),
        "sort_options": get_sort_options(
            File.sort_options, debug=request.session.get("DEBUG")
        ),
        "guide_words": True
    }

    default_sort = None

    # Pull files based on page
    qs = File.objects.search(request.GET)
    if details:
        qs = qs.filter(details__in=details)
        if len(details) == 1:
            d = Detail.objects.get(pk=details[0])
            data["title"] = "Browse - " + d.detail
            data["header"] = data["title"]
    if letter:
        qs = qs.filter(letter=letter)
        data["title"] = "Browse - " + letter.upper()
        data["header"] = data["title"]
    if request.path == "/new/":
        data["title"] = "New Additions"
        data["header"] = data["title"]
        data["sort_options"] = []
        data["sort"] = "-publish_date"
        default_sort = ["-publish_date", "-id"]
    elif request.path == "/new-releases/":
        data["title"] = "New Releases"
        data["header"] = data["title"]
        data["sort_options"] = []
        default_sort = ["-release_date", "-id"]
    elif request.path == "/uploaded/":
        data["title"] = "Upload Queue"
        data["prefix_template"] = "museum_site/prefixes/upload-queue.html"

        # Add sort by upload date
        data["sort_options"] = (
            [{"text": "Upload Date", "val": "uploaded"}] + data["sort_options"]
        )
        default_sort = ["-id"]
    elif request.path == "/featured/":
        data["title"] = "Featured Worlds"
        data["extras"] = ["museum_site/blocks/extra-featured-world.html"]
    elif request.path == "/roulette/":
        if not request.GET.get("seed"):
            return redirect("/roulette?seed={}".format(int(request.GET.get("seed", time()))))

        data["title"] = "Roulette"
        data["rng_seed"] = request.GET.get("seed")
        data["prefix_template"] = "museum_site/prefixes/roulette.html"

        # Add sort by random
        data["sort_options"] = (
            [{"text": "Random", "val": "random"}] + data["sort_options"]
        )

        qs = File.objects.roulette(data["rng_seed"], PAGE_SIZE)

    if request.GET.get("sort") == "title":
        qs = qs.order_by("sort_title")
    elif request.GET.get("sort") == "author":
        qs = qs.order_by("author")
    elif request.GET.get("sort") == "company":
        qs = qs.order_by("company")
    elif request.GET.get("sort") == "rating":
        qs = qs.order_by("-rating")
    elif request.GET.get("sort") == "release":
        qs = qs.order_by("release_date")
    elif request.GET.get("sort") == "-release":
        qs = qs.order_by("-release_date")
    elif request.GET.get("sort") == "uploaded":
        qs = qs.order_by("-id")
    elif default_sort:
        qs = qs.order_by(*default_sort)

    qs = qs.prefetch_related("upload_set").distinct()

    data = get_pagination_data(request, data, qs)

    if data["page"].object_list:
        data["first_item"] = data["page"].object_list[0]
        data["last_item"] = (
            data["page"].object_list[len(data["page"].object_list) - 1]
        )

    # Show description for certain views
    if DETAIL_LOST in details:
        data["show_description"] = True

    return render(request, "museum_site/generic-directory.html", data)


def file_download(request, letter, filename):
    """ Returns page listing all download locations with a provided file """
    data = {}
    data["file"] = get_object_or_404(File, letter=letter, filename=filename)
    data["title"] = data["file"].title + " - Downloads"
    data["downloads"] = data["file"].downloads.all()
    data["letter"] = letter

    return render(request, "museum_site/download.html", data)


def file_articles(request, letter, filename):
    """ Returns page listing all articles associated with a provided file. """
    data = {}
    data["file"] = get_object_or_404(File, letter=letter, filename=filename)
    data["title"] = data["file"].title + " - Articles"
    data["articles"] = data["file"].articles.not_removed()
    data["letter"] = letter

    return render(request, "museum_site/article.html", data)


def file_viewer(request, letter, filename, local=False):
    """ Returns page exploring a file's zip contents """
    data = {}
    data["custom_layout"] = "fv-grid"
    data["year"] = YEAR
    data["details"] = []  # Required to show all download links
    data["local"] = local
    data["files"] = []
    if not local:
        res = File.objects.identifier(letter=letter, filename=filename)
        matches = len(res)
        if matches == 1:
            data["file"] = res[0]
        else:
            return redirect("/search?filename={}&err=404".format(filename))

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

        if ".zip" in filename.lower():
            zip_file = zipfile.ZipFile(
                os.path.join(SITE_ROOT, "zgames", letter, filename)
            )
            files = zip_file.namelist()
            files.sort(key=str.lower)
            data["zip_info"] = sorted(
                zip_file.infolist(), key=lambda k: k.filename.lower()
            )
            data["zip_comment"] = zip_file.comment.decode("latin-1")
            # TODO: "latin-1" may or may not actually be the case

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

    # Sort files into ZZT, Super ZZT, SAV, BRD, and non-ZZT extensions
    all_files = {"zzt": [], "szzt": [], "sav": [], "brd": [], "misc": []}
    keys = list(all_files.keys())
    for fname in data["files"]:
        ext = fname.split(".")[-1].lower()
        if ext in keys:
            all_files[ext].append(fname)
        else:
            all_files["misc"].append(fname)
    data["files"] = []
    for k in keys:
        sorted(all_files[k])
        data["files"] += all_files[k]

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
        else:
            data["charsets"] = CHARSETS
            data["custom_charsets"] = CUSTOM_CHARSETS
    # TODO LOCAL FILES CAN'T GET CHARSETS WITH THIS
    else:
        data["charsets"] = CHARSETS
        data["custom_charsets"] = CUSTOM_CHARSETS

    return render(request, "museum_site/file.html", data)


def get_file_by_pk(request, pk):
    data = {}
    f = get_object_or_404(File, pk=pk)
    return redirect(f.attributes_url())


def review(request, letter, filename):
    data = {}
    today = datetime.now()
    zfile = File.objects.identifier(
        letter=letter, filename=filename
    ).first()
    reviews = Review.objects.filter(zfile_id=zfile.id)
    data["letter"] = letter
    data["title"] = zfile.title + " - Reviews"

    review_form = ReviewForm()

    # Prevent doubling up on reviews
    recent = reviews.filter(
        ip=request.META.get("REMOTE_ADDR"),
        date=today
    )
    if recent:
        data["recent"] = recent[0].pk
    elif request.method == "POST" and zfile.can_review:
        if request.META["REMOTE_ADDR"] in BANNED_IPS:
            return HttpResponse("Banned account.")

        review_form = ReviewForm(request.POST)

        if review_form.is_valid():
            print(review_form.cleaned_data.keys())

            # Create and prepare new Upload object
            review = review_form.save(commit=False)
            if request.user.is_authenticated:
                review.author = ""
                review.user_id = request.user.id
            review.ip = request.META.get("REMOTE_ADDR")
            review.date = today
            review.zfile_id = zfile.id
            review.save()

            # Update file's review count/scores
            zfile.calculate_reviews()
            zfile.save()

            # Make Announcement
            discord_announce_review(review)

    if request.user.is_authenticated:
        del review_form.fields["author"]

    data["reviews"] = reviews
    data["today"] = today
    data["file"] = zfile
    data["form"] = review_form
    return render(request, "museum_site/file-review.html", data)

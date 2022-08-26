from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from museum_site.common import *
from museum_site.constants import *
from museum_site.core import *
from museum_site.forms import ReviewForm
from museum_site.models import *


def file_attributes(request, key):
    data = {}

    if key.lower().endswith(".zip"):  # Try old URLs with zip in them -- TODO MAY 24 confirm this is still the best solution
        return redirect_with_querystring("file_attributes", request.META.get("QUERY_STRING"), key=key[:-4])

    data["file"] = get_object_or_404(File, key=key)
    data["file"].init_actions()
    data["upload_info"] = Upload.objects.filter(file_id=data["file"]).first()
    data["reviews"] = Review.objects.filter(
        zfile__id=data["file"].pk
    ).defer("content")
    data["title"] = data["file"].title + " - Attributes"

    return render(request, "museum_site/attributes.html", data)


def file_download(request, key):
    """ Returns page listing all download locations with a provided file """
    data = {}

    if key.lower().endswith(".zip"):  # Try old URLs with zip in them
        return redirect_with_querystring("file_download", request.META.get("QUERY_STRING"), letter=letter, key=key[:-4])

    data["file"] = get_object_or_404(File, key=key)
    data["title"] = data["file"].title + " - Downloads"
    data["downloads"] = data["file"].downloads.all()
    data["letter"] = data["file"].letter

    return render(request, "museum_site/download.html", data)


def file_viewer(request, key, local=False):
    """ Returns page exploring a file's zip contents """
    data = {
        "content_classes": ["fv-grid"],
        "details": [],
        "local": local,
        "files": [],
    }

    if not local:
        qs = File.objects.filter(key=key)
        if len(qs) == 1:
            data["file"] = qs[0]
        else:
            if key.lower().endswith(".zip"):  # Try old URLs with zip in them
                return redirect_with_querystring("file", request.META.get("QUERY_STRING"), key=key[:-4])
            else:
                return redirect("/search?filename={}&err=404".format(key))

        # Check for explicit flag/permissions
        if data["file"].explicit:
            check = explicit_redirect_check(request, data["file"].pk)
            if check != "NO-REDIRECT":
                return check

        data["title"] = data["file"].title
        data["letter"] = data["file"].letter

        # Check for recommended custom charset
        for charset in CUSTOM_CHARSETS:
            if data["file"].id == charset["id"]:
                data["custom_charset"] = charset["filename"]
                break

        if data["file"].is_detail(DETAIL_UPLOADED):
            letter = "uploaded"
            data["uploaded"] = True

        zip_file = zipfile.ZipFile(
            data["file"].phys_path()
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
            if (f and f[-1] != os.sep and not f.startswith("__MACOSX" + os.sep) and not f.upper().endswith(".DS_STORE")):
                data["files"].append(f)
        data["load_file"] = urllib.parse.unquote(
            request.GET.get("file", "")
        )
        data["load_board"] = request.GET.get("board", "")
    else:  # Local files
        data["file"] = "Local File Viewer"
        data["letter"] = ""

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
        if data["file"].is_detail(DETAIL_ZZT):
            for charset in CHARSETS:
                if charset["engine"] == "ZZT":
                    data["charsets"].append(charset)
            for charset in CUSTOM_CHARSETS:
                if charset["engine"] == "ZZT":
                    data["custom_charsets"].append(charset)
        elif data["file"].is_detail(DETAIL_SZZT):
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


def review(request, key):
    data = {
        "sort_options": [
            {"text": "Review Date (Newest)", "val": "-date"},
            {"text": "Review Date (Oldest)", "val": "date"},
            {"text": "Rating", "val": "-rating"},
        ],
        "sort": request.GET.get("sort")
    }

    if not request.session.get("REVIEW_PROFANITY_FILTER"):
        request.session["REVIEW_PROFANITY_FILTER"] = "on"
    if request.GET.get("pf"):
        request.session["REVIEW_PROFANITY_FILTER"] = request.GET.get("pf")

    today = datetime.now().date()
    zfile = File.objects.filter(key=key).first()
    if key.lower().endswith(".zip"):  # Try old URLs with zip in them
        return redirect_with_querystring("reviews", request.META.get("QUERY_STRING"), key=key[:-4])

    sort_keys = {
        "date": "date",
        "-date": "-date",
        "-rating": "-rating",
    }

    # Fix for logged out users seeing pending logged out reviews
    your_user_id = request.user.id
    if your_user_id is None:
        your_user_id = -32767

    reviews = Review.objects.filter(
        (
            Q(approved=True) |
            Q(ip=request.META["REMOTE_ADDR"]) |
            Q(user_id = your_user_id)
        ),
        zfile_id=zfile.id,
    )

    # Sort queryset
    reviews = sort_qs(reviews, data["sort"], sort_keys, default_sort="rating")

    data["letter"] = zfile.letter
    data["title"] = zfile.title + " - Reviews"

    review_form = ReviewForm()
    if request.user.is_authenticated:
        del review_form.fields["author"]

    # Prevent doubling up on reviews
    recent = reviews.filter(
        ip=request.META.get("REMOTE_ADDR"),
        date=today
    )
    if recent:
        data["recent"] = recent[0].pk
    elif request.method == "POST" and zfile.can_review != File.REVIEW_NO:
        if banned_ip(request.META["REMOTE_ADDR"]):
            return HttpResponse("Banned account.")

        review_form = ReviewForm(request.POST)

        if request.user.is_authenticated:
            del review_form.fields["author"]

        if review_form.is_valid():
            # Create and prepare new Review object
            review = review_form.save(commit=False)
            if request.user.is_authenticated:
                review.author = request.user.username
                review.user_id = request.user.id
            review.ip = request.META.get("REMOTE_ADDR")
            review.date = today
            review.zfile_id = zfile.id

            if review.zfile.can_review == File.REVIEW_APPROVAL or (review.content.find("href") != -1):
                review.approved = False
            review.save()

            # Update file's review count/scores if the review is approved
            if review.zfile.can_review == File.REVIEW_YES and review.approved == True:
                zfile.calculate_reviews()
                # Make Announcement
                discord_announce_review(review)
                zfile.save()

    data["reviews"] = reviews
    data["today"] = today
    data["file"] = zfile
    data["form"] = review_form
    return render(request, "museum_site/file-review.html", data)

from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from .common import *
from .constants import *
from .models import *
from .private import BANNED_IPS


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

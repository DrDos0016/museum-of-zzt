from datetime import datetime

from django.core.cache import cache
from django.conf import settings

from museum_site.constants import TERMS_DATE, CSS_INCLUDES, BOOT_TS, EMAIL_ADDRESS
from museum_site.core.detail_identifiers import *
from museum_site.models.file import File


def museum_global(request):
    data = {}

    # Not the full list, just what's currently needed
    data["DETAIL"] = {
        "LOST": DETAIL_LOST,  # file-review.html
        "UPLOADED": DETAIL_UPLOADED,  # file-review.html
        "WEAVE": DETAIL_WEAVE,  # file.html
    }

    # Debug mode
    if settings.DEBUG or request.GET.get("DEBUG") or request.session.get("DEBUG"):
        data["debug"] = True
    else:
        data["debug"] = False

    # Server info
    data["HOST"] = request.get_host()
    data["ENV"] = cache.get("ENV")
    data["PROTOCOL"] = "https" if request.is_secure() else "http"
    data["DOMAIN"] = data["PROTOCOL"] + "://" + data["HOST"]

    # Server date/time
    data["datetime"] = datetime.utcnow()
    if data["datetime"].day == 27:  # Drupe Day
        data["drupe"] = True
    if (data["datetime"].day == 1 and data["datetime"].month == 4) or request.GET.get("april"):  # April 1st
        data["april"] = True

    # E-mail
    data["EMAIL_ADDRESS"] = EMAIL_ADDRESS
    data["BOOT_TS"] = BOOT_TS

    # CSS Files
    data["CSS_INCLUDES"] = CSS_INCLUDES

    # Featured Worlds
    data["fg"] = File.objects.featured_worlds().order_by("?").first()
    if request.GET.get("fgid"):
        data["fg"] = File.objects.reach(pk=int(request.GET["fgid"]))

    data["fg"] = data["fg"]

    # Queue size
    data["UPLOAD_QUEUE_SIZE"] = cache.get("UPLOAD_QUEUE_SIZE", "-")

    # User TOS Date checks
    if request.user.is_authenticated:
        if (TERMS_DATE > request.user.profile.accepted_tos and request.method == "GET" and request.path != "/user/update-tos/"):
            # Force a new login
            for key in ["_auth_user_id", "_auth_user_backend", "_auth_user_hash"]:
                if request.session.get(key):
                    del request.session[key]
            data["forced_logout"] = True
    return data

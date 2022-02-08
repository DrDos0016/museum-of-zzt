from datetime import datetime

from museum_site.detail import Detail
from museum_site.file import File
from museum_site.constants import DETAIL_FEATURED, DETAIL_UPLOADED, TERMS_DATE
from museum_site.common import (
    DEBUG, EMAIL_ADDRESS, BOOT_TS, CSS_INCLUDES, UPLOAD_CAP, env_from_host,
    qs_sans
)


def museum_global(request):
    data = {}

    # Debug mode
    if DEBUG or request.GET.get("DEBUG") or request.session.get("DEBUG"):
        data["debug"] = True
    else:
        data["debug"] = False

    # Server info
    data["HOST"] = request.get_host()
    data["ENV"] = env_from_host(data["HOST"])
    data["PROTOCOL"] = "https" if request.is_secure() else "http"
    data["DOMAIN"] = data["PROTOCOL"] + "://" + data["HOST"]

    # Server date/time
    data["datetime"] = datetime.utcnow()
    if data["datetime"].day == 27:  # Drupe Day
        data["drupe"] = True
    if data["datetime"].day == 1 and data["datetime"].month == 4:  # April 1st
        data["april"] = True

    # Common query string modifications
    data["qs_sans_page"] = qs_sans(request.GET, "page")
    data["qs_sans_view"] = qs_sans(request.GET, "view")
    data["qs_sans_both"] = qs_sans(request.GET, ["page", "view"])

    # E-mail
    data["EMAIL_ADDRESS"] = EMAIL_ADDRESS
    data["BOOT_TS"] = BOOT_TS

    # CSS Files
    data["CSS_INCLUDES"] = CSS_INCLUDES

    # Featured Worlds
    data["fg"] = File.objects.featured_worlds().order_by("?").first()
    if request.GET.get("fgid"):
        data["fg"] = File.objects.reach(pk=int(request.GET["fgid"]))

    # Upload Cap
    data["UPLOAD_CAP"] = UPLOAD_CAP

    # Queue size
    if (not request.session.get("FILES_IN_QUEUE") or (request.path in [
        "/", "/uploaded/", "/upload/", "/upload/complete"
    ])):
        request.session["FILES_IN_QUEUE"] = File.objects.unpublished().count()

    # User TOS Date checks
    if request.user.is_authenticated:
        if (
            TERMS_DATE > request.user.profile.accepted_tos and
            request.method == "GET" and
            request.path != "/user/update-tos/"
        ):
            # Force a new login
            for key in [
                "_auth_user_id", "_auth_user_backend", "_auth_user_hash"
            ]:
                if request.session.get(key):
                    del request.session[key]
    return data

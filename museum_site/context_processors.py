from datetime import datetime

from museum_site.detail import Detail
from museum_site.file import File
from museum_site.constants import DETAIL_FEATURED, DETAIL_UPLOADED
from museum_site.common import DEBUG, EMAIL_ADDRESS, BOOT_TS, CSS_INCLUDES, UPLOAD_CAP, env_from_host


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
    if data["datetime"].day == 27:  # This is very important
        data["drupe"] = True
    if data["datetime"].day == 1 and data["datetime"].month == 4:  # This is very important
        data["april"] = True

    # E-mail
    data["EMAIL_ADDRESS"] = EMAIL_ADDRESS
    data["BOOT_TS"] = BOOT_TS

    # CSS Files
    data["CSS_INCLUDES"] = CSS_INCLUDES

    # Featured Games
    featured = Detail.objects.get(pk=DETAIL_FEATURED)
    data["fg"] = featured.file_set.all().order_by("?")[0]

    # Upload Cap
    data["UPLOAD_CAP"] = UPLOAD_CAP

    # Queue size
    if not request.session.get("FILES_IN_QUEUE"):
        request.session["FILES_IN_QUEUE"] = File.objects.filter(details__id__in=[DETAIL_UPLOADED]).count()
    return data

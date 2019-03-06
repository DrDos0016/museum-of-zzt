from datetime import datetime

from museum_site.models import Detail, DETAIL_FEATURED
from museum_site.common import DEBUG, EMAIL_ADDRESS, BOOT_TS


def museum_global(request):
    use_debug = True if (DEBUG or request.GET.get("DEBUG")) else False
    data = {"debug": use_debug}

    # Server info
    data["HOST"] = request.get_host()
    if data["HOST"] in ["beta.museumofzzt.com"]:
        data["ENV"] = "BETA"
    elif data["HOST"] in ["museumofzzt.com"]:
        data["ENV"] = "PROD"
    else:
        data["ENV"] = "DEV"

    data["PROTOCOL"] = "https" if request.is_secure() else "http"
    data["DOMAIN"] = data["PROTOCOL"] + "://" + data["HOST"]

    # Server date/time
    data["datetime"] = datetime.utcnow()
    if data["datetime"].day == 27:  # This is very important
        data["drupe"] = True

    # E-mail
    data["EMAIL_ADDRESS"] = EMAIL_ADDRESS
    data["BOOT_TS"] = BOOT_TS

    # Featured Games
    featured = Detail.objects.get(pk=DETAIL_FEATURED)
    data["fg"] = featured.file_set.all().order_by("?")[0]
    return data

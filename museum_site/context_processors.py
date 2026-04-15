from datetime import datetime, UTC
from random import choice

from django.core.cache import cache
from django.conf import settings
from django.urls import resolve, reverse

from museum_site.constants import TERMS_DATE, CSS_INCLUDES, BOOT_TS, EMAIL_ADDRESS
from museum_site.core.detail_identifiers import *
from museum_site.models.file import File

from museum_site.core.character_sets import init_standard_charsets, init_custom_charsets

def museum_global(request):
    data = {}

    # Cache init
    data["ENV"] = cache.get_or_set("ENV", settings.ENVIRONMENT)
    if not cache.get("CHARSETS") or not cache.get("CUSTOM_CHARSETS"):
        init_standard_charsets()
        init_custom_charsets()

    # Base Template
    if request.path.startswith("/tools/"):
        data["BASE_TEMPLATE"] = "museum_site/tools/tool-main.html"
    else:
        data["BASE_TEMPLATE"] = "museum_site/main.html"

    # Resolved URL
    if request.resolver_match:
        data["resolved_url"] = resolve(request.path)

    # Debug mode
    data["debug"] = True if (settings.DEBUG or request.GET.get("DEBUG") or request.session.get("DEBUG")) else False

    # Server info
    data["HOST"] = request.get_host()
    data["PROTOCOL"] = "https" if request.is_secure() else "http"
    data["DOMAIN"] = data["PROTOCOL"] + "://" + data["HOST"]

    # Logo Path
    logo_path_mods = {"DEV": "-INVERTED", "BETA": "-BETA"}
    data["logo_path"] = "chrome/logos/museum-logo-by-lazymoth{}.png".format(logo_path_mods.get(data["ENV"], ""))

    # Server date/time
    data["datetime"] = datetime.now(UTC)
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
    DEFAULT_SPOTLIGHT_SOURCES = ["spotlight-beginner-friendly", "spotlight-new-releases", "spotlight-featured-worlds", "spotlight-best-of-zzt"]
    spotlight_sources = request.session.get("spotlight_sources", DEFAULT_SPOTLIGHT_SOURCES)
    spotlight_collection_sources = request.session.get("spotlight_collection_sources", [])
    if ("spotlight-custom" in spotlight_sources) and not spotlight_collection_sources:
        spotlight_sources.remove("spotlight-custom")

    source = choice(spotlight_sources) if spotlight_sources else choice(DEFAULT_SPOTLIGHT_SOURCES)
    spotlight_collection_source = choice(spotlight_collection_sources) if source == "spotlight-custom" else None
    data["spotlight_source"] = source
    data["spotlight_collection_source"] = spotlight_collection_source

    if request.GET.get("fgid"):
        data["fg"] = File.objects.reach(pk=int(request.GET["fgid"]))
    else:
        data["fg"] = File.objects.get_spotlight_world(source, spotlight_collection_source).order_by("?").first()

    if not data["fg"]:
        data["fg"] = File.objects.filter(pk=1015).first()  # ZZT v3.2

    # Queue size
    data["UPLOAD_QUEUE_SIZE"] = cache.get_or_set("UPLOAD_QUEUE_SIZE", File.objects.unpublished().count)

    # Active Tool
    data["active_tool"] = request.session.get("active_tool")
    data["active_tool_template"] = request.session.get("active_tool_template")

    # User TOS Date checks
    if request.user.is_authenticated:
        if (TERMS_DATE > request.user.profile.accepted_tos and request.method == "GET" and request.path != reverse("update_tos")):
            # Force a new login
            for key in ["_auth_user_id", "_auth_user_backend", "_auth_user_hash"]:
                if request.session.get(key):
                    del request.session[key]
            data["forced_logout"] = True
    return data

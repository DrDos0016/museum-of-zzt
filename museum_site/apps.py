from django.core.cache import cache
import os

from django.apps import AppConfig
from django.db.utils import ProgrammingError
from django import VERSION as DJANGO_VERSION
from sys import version
from datetime import datetime

NONREPO_CONTENT = [
    "backups/", "zookeeper/",
    "museum_site/private.py",
    "museum_site/static/data/mass_dl.json",
]


class Museum_Site_Config(AppConfig):
    name = "museum_site"
    verbose_name = "Museum of ZZT"

    def ready(self):
        from museum_site.models import File
        from museum_site.signals import article_post_save
        from museum_site.core.character_sets import init_charsets

        now = datetime.utcnow()
        site_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        print("================== Museum of ZZT Startup ===================")
        print("Python      :", version.split(" ")[0])
        print("Django      :", ".".join(map(str, DJANGO_VERSION)))
        print("Server Time :", now)
        print("Site Root   :", site_root)
        if os.path.isfile(os.path.join(site_root, "DEV")):
            print("Environment : DEV")
        if os.path.isfile(os.path.join(site_root, "BETA")):
            print("Environment : BETA")
        if os.path.isfile(os.path.join(site_root, "PROD")):
            print("Environment : PROD")

        # Check for non-repo content
        missing = []
        for name in NONREPO_CONTENT:
            if not os.path.exists(name):
                missing.append(name)
        if missing:
            print("------------ Missing Non-Repository Content -----------")
            for m in missing:
                print(m)

        # Initialize cache
        print("-------------------- Initializing Cache --------------------")
        INITIAL_CACHE = {}

        try:
            INITIAL_CACHE["UPLOAD_QUEUE_SIZE"] = File.objects.unpublished().count()
        except ProgrammingError:
            pass

        for (k, v) in INITIAL_CACHE.items():
            cache.set(k, v)
            print("{:<25}: {}".format(k, v))

        # Initialize character sets
        print("--------------- Initializing Character Sets ----------------")
        (standard_charsets, custom_charsets) = init_charsets(site_root=site_root)
        print("{} standard character sets found".format(len(standard_charsets)))
        print("{} custom character sets found".format(len(custom_charsets)))
        cache.set("CHARSETS", standard_charsets)
        cache.set("CUSTOM_CHARSETS", custom_charsets)

        print("==================== Startup Complete ======================")

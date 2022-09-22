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

        print("==================== Startup Complete ======================")

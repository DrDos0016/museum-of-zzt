from django.core.cache import cache
import os

from django.apps import AppConfig
from django import VERSION as DJANGO_VERSION
from sys import version
from datetime import datetime


class Museum_Site_Config(AppConfig):
    name = "museum_site"
    verbose_name = "Museum of ZZT"

    def ready(self):
        from museum_site.models import File

        now = datetime.utcnow()
        site_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Initial cache values
        cache.set("UPLOAD_QUEUE_SIZE", File.objects.unpublished().count())

        print("================== Museum of ZZT Startup ===================")
        print("Python      :", version.split(" ")[0])
        print("Django      :", ".".join(map(str, DJANGO_VERSION)))
        print("Server Time :", now)
        print("Site Root   :", site_root)
        print("-------------------- Initializing Cache --------------------")
        print("UPLOAD_QUEUE_SIZE         :", cache.get("UPLOAD_QUEUE_SIZE"))
        print("==================== Startup Complete ======================")

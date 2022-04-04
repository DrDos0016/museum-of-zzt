import os

from django.apps import AppConfig
from django import VERSION as DJANGO_VERSION
from sys import version
from datetime import datetime

class Museum_Site_Config(AppConfig):
    name = "museum_site"
    verbose_name = "Museum of ZZT"

    def ready(self):
        now = datetime.utcnow()
        site_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print("================== Museum of ZZT Startup ===================")
        print("Python      :", version.split(" ")[0])
        print("Django      :", ".".join(map(str, DJANGO_VERSION)))
        print("Server Time :", now)
        print("Site Root   :", site_root)
        print("==================== Startup Complete ======================")

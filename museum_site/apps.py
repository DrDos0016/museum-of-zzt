from django.core.cache import cache
from django.db.utils import ProgrammingError
import os

from django.apps import AppConfig
from django.conf import settings
from django.db.utils import ProgrammingError
from django import VERSION as DJANGO_VERSION
from sys import version, exit
from datetime import datetime, UTC


class Museum_Site_Config(AppConfig):
    name = "museum_site"
    verbose_name = "Museum of ZZT"

    def ready(self):
        self.museum_startup()
        self.check_secret_key()
        self.check_non_repo_content()
        print("==================== Startup Complete ======================")

    def museum_startup(self):
        self.now = datetime.now(UTC)
        self.site_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print("================== Museum of ZZT Startup ===================")
        print("Python      :", version.split(" ")[0])
        print("Django      :", ".".join(map(str, DJANGO_VERSION)))
        print("Server Time :", self.now)
        print("Site Root   :", self.site_root)
        print("Environment :", settings.ENVIRONMENT)
        print("============================================================")

    def check_secret_key(self):
        if settings.SECRET_KEY == "!c;LOCKED FILE":
            print("!!! YOU ARE USING THE PLACEHOLDER SECRET KEY !!!")
            print("Please set the environment variable MOZ_SECRET_KEY")
            if settings.ENVIRONMENT != "DEV":
                exit()

    def check_non_repo_content(self):
        NONREPO_CONTENT = ["backups/", "zookeeper/", "museum_site/static/data/mass_dl.json"]
        missing = []
        for name in NONREPO_CONTENT:
            if not os.path.exists(name):
                missing.append(name)
                if len(missing) == 1:
                    print("------------ Missing Non-Repository Content -----------")
                print(name)

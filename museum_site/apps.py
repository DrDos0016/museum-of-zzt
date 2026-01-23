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
        print("==================== Startup Complete ======================")

    def museum_startup(self):
        self.now = datetime.now(UTC)
        print("================== Museum of ZZT Startup ===================")
        print("Python      :", version.split(" ")[0])
        print("Django      :", ".".join(map(str, DJANGO_VERSION)))
        print("Server Time :", self.now)
        print("Site Root   :", settings.BASE_DIR)
        print("Environment :", settings.ENVIRONMENT)
        print("==================== Optional Libraries ====================")
        print("Zeta        :", self.has_zeta_install())
        print("Zookeeper   :", self.has_zookeeper_install())

    def has_zeta_install(self):
        zeta_path = os.path.join(settings.BASE_DIR, "museum_site", "static", "zeta86")
        return "Found" if os.path.exists(zeta_path) else "Missing"

    def has_zookeeper_install(self):
        try:
            from zookeeper.constants import ZZT_IDENTIFIER
            return "Found"
        except ImportError:
            return "Missing"
        return "Missing"

    def check_secret_key(self):
        if settings.SECRET_KEY == "!c;LOCKED FILE":
            print("!!! YOU ARE USING THE PLACEHOLDER SECRET KEY !!!")
            print("Please set the environment variable MOZ_SECRET_KEY")
            if settings.ENVIRONMENT != "DEV":
                exit()

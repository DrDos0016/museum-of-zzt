import os

from datetime import datetime, timezone

from django.apps import AppConfig

from museum_site.constants import SITE_ROOT


class ZapConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'zap'
    verbose_name = "Zero-Effort Auto Poster"

    def ready(self):
        now = datetime.now(timezone.utc)
        year = str(now.year)
        zap_static_root = os.path.join(SITE_ROOT, "museum_site", "static", "zap")
        zap_media_path = os.path.join(zap_static_root, "media")
        zap_renders_path = os.path.join(zap_static_root, "renders")
        print("=========================== ZAP ============================")
        print("Checking for missing media directories...")
        if not os.path.isdir(zap_media_path):
            print("Creating", zap_media_path)
            os.makedirs(zap_media_path)
        if not os.path.isdir(zap_renders_path):
            print("Creating", zap_renders_path)
            os.makedirs(zap_renders_path)
        if not os.path.isdir(os.path.join(zap_media_path, year)):
            print("Creating", os.path.join(zap_media_path, year), "and subdirectories")
            os.mkdir(os.path.join(zap_media_path, year))
            for m in range(1,13):
                os.mkdir(os.path.join(zap_media_path, year, str(m).zfill(2)))
        print("================== ZAP Startup Complete ====================")

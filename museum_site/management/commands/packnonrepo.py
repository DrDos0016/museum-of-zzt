import os
import tarfile

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

#from museum_site.constansts import ZGAMES_BASE_PATH


class Command(BaseCommand):
    #https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/
    help = "Compresses defined non-repository content [zgames|articles|data|<app's_static_dir>]."

    def add_arguments(self, parser):
        parser.add_argument("items", nargs="+",)

    def handle(self, *args, **options):
        print(settings.BASE_DIR)
        for item in options["items"]:
            print("Compressing", item)
            tar = tarfile.open(item + ".tar.gz", "w:gz")

            # Specific Content
            if item == "zgames":
                tar_path = item
                item_path = os.path.join(settings.BASE_DIR, tar_path)
            elif item == "articles":
                tar_path = os.path.join("museum_site", "static", "articles")
                item_path = os.path.join(settings.BASE_DIR, tar_path)
            elif item == "data":
                tar_path = os.path.join("museum_site", "static", "data")
                item_path = os.path.join(settings.BASE_DIR, tar_path)
            elif item == "credits":
                tar_path = os.path.join("museum_site", "static", "credits")
                item_path = os.path.join(settings.BASE_DIR, tar_path)
            else:
                # Compress /static/ directory
                tar_path = os.path.join(item, "static", item)
                item_path = os.path.join(settings.BASE_DIR, tar_path)
            tar.add(item_path, tar_path)

            self.stdout.write(self.style.SUCCESS("Success"))

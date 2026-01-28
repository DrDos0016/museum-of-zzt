import os
import shutil
import tempfile
import zipfile

from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string

from museum_site.core.detail_identifiers import *
from museum_site.models import *


class Command(BaseCommand):
    # https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/
    help = "Creates a set of Zip files for the Mass Download page"
    bucket_labels_year = ["UNKNOWN"] + list(range(1991, 2010)) + ["2010-2019"] + ["2020-2024"] + ["2025-2029"]
    bucket_labels_special = ["szzt_worlds", "weave_worlds", "zig_worlds", "utilities", "zzm_audio", "featured_worlds", "misc"]
    template_names = {"szzt_worlds": "szzt", "weave_worlds": "weave", "zig_worlds": "zig", "utilities": "utilities", "zzm_audio": "zzm", "featured_worlds": "featured"}  # years use 'zzt'

    buckets = {}
    all_zfiles = None
    TEMP_DIR = tempfile.TemporaryDirectory(prefix="moz-")
    TEMP_DIR_PATH = TEMP_DIR.name
    missing = []  # List of ZFile objects which do not have a zipfile available
    to_move = []  # File paths of zipfiles to be placed into /zgames/
    excluded = []  # List of ZFile objects that have zipfiles but were not put in a bucket

    def handle(self, *args, **options):
        print("===== Mass DL Zip File Generator =====")
        print("Created temporary directory", self.TEMP_DIR_PATH)
        self.all_zfiles = File.objects.all().order_by("year", "release_date", "sort_title")
        print(len(self.all_zfiles), "ZFiles to process")
        self.generate_buckets()
        self.fill_buckets()
        self.buckets_to_zips()
        self.move_zips_to_zgames()
        print("DONE.")

    def add_to_bucket(self, key, zf, prefix=True):
        if prefix:
            bucket_key = "zzt_worlds_" + str(key)
        else:
            bucket_key = key

        # Check that there's a zipfile to compile
        if zf.can_museum_download:
            self.buckets[bucket_key].append(zf)
            print("  +", bucket_key)
            self.added_current_zf = True
        else:
            print("  ? NO ZIPFILE EXISTS. FILE WILL BE IGNORED")
            self.missing.append(zf)
        return True

    def generate_buckets(self):
        prefix = "zzt_worlds_{}"
        for category in self.bucket_labels_year:
            bucket_name = prefix.format(category)
            self.buckets[bucket_name] = []
            print("Created bucket", bucket_name)

        # Specialty Buckets (ooh la la)
        for special_bucket in self.bucket_labels_special:
            self.buckets[special_bucket] = []
            print("Created bucket", special_bucket)

    def fill_buckets(self):
        for zf in self.all_zfiles:
            self.added_current_zf = False
            print(str(zf.pk).zfill(4), "[" + zf.key + "]", zf.title)
            # ZZT Worlds are put into years
            if zf.is_detail(DETAIL_ZZT):
                if zf.year is None or zf.year.year < 1991:
                    self.add_to_bucket("UNKNOWN", zf)
                else:
                    if zf.year.year < 2010:
                        self.add_to_bucket(zf.year.year, zf)
                    elif zf.year.year < 2020:
                        self.add_to_bucket("2010-2019", zf)
                    elif zf.year.year < 2025:
                        self.add_to_bucket("2020-2024", zf)
                    elif zf.year.year < 2029:
                        self.add_to_bucket("2025-2029", zf)

            if zf.is_detail(DETAIL_SZZT):  # Super ZZT Worlds
                self.add_to_bucket("szzt_worlds", zf, prefix=False)

            if zf.is_detail(DETAIL_WEAVE):  # Weave Worlds
                self.add_to_bucket("weave_worlds", zf, prefix=False)

            if zf.is_detail(DETAIL_ZIG):  # ZIG Worlds
                self.add_to_bucket("zig_worlds", zf, prefix=False)

            if zf.is_detail(DETAIL_UTILITY):  # Utilities
                self.add_to_bucket("utilities", zf, prefix=False)

            if zf.is_detail(DETAIL_ZZM):  # ZZM
                self.add_to_bucket("zzm_audio", zf, prefix=False)

            if zf.is_detail(DETAIL_FEATURED):  # Featured Worlds
                self.add_to_bucket("featured_worlds", zf, prefix=False)

            if not self.added_current_zf:  # No bucket
                self.add_to_bucket("misc", zf, prefix=False)
                self.excluded.append(zf)

        print("Buckets have been filled.")
        print("{} zfiles are missing zips and will not be included in any mass download.".format(len(self.missing)))
        for missing in self.missing:
            print("MISSING -", missing)
        print("{} zfiles will be placed in the miscellaneous bucket.".format(len(self.excluded)))
        for excluded in self.excluded:
            print("MISC - ", excluded)

        return True

    def buckets_to_zips(self):
        for zip_name, contents in self.buckets.items():
            print("Processing files for {}. {} files to process.".format(zip_name, len(contents)))

            print("Creating {}.zip".format(zip_name))
            zip_path = os.path.join(self.TEMP_DIR_PATH, zip_name + ".zip")
            self.to_move.append(zip_path)
            mass_zip = zipfile.ZipFile(zip_path, "w")
            print("  Adding files...")
            processed_zfiles = []
            for zf in contents:
                mass_zip.write(zf.phys_path(), arcname=os.path.basename(zf.phys_path()))

                # Figure out date to display
                zf.zfile_date = ""
                if zf.release_date:
                    zf.zfile_date = str(zf.release_date)[:10]
                elif zf.year:
                    zf.zfile_date = str(zf.year.year) + " (approx.)"
                else:
                    zf.zfile_date = "Unknown Date"

                # Figure out authors
                zf.author_str = ", ".join(zf.related_list("authors"))
                processed_zfiles.append(zf)

            readme_context = {
                "year": zip_name.replace("zzt_worlds_", ""),
                "zfiles": processed_zfiles,
                "readme_timestamp": datetime.now()
            }

            readme_template = "museum_site/subtemplate/mass-dl/mass-dl-{}.html".format(self.template_names.get(zip_name, "zzt"))

            try:
                readme_body = render_to_string(readme_template, readme_context).strip()
            except:
                print("  MISSING TEMPLATE", zip_name, readme_template)
                continue
            readme_path = os.path.join(self.TEMP_DIR_PATH, "Museum of ZZT Collection - " + zip_name + ".txt")
            print("  Writing README {}...".format(readme_path))
            with open(readme_path, "w") as fh:
                fh.write(readme_body)
            mass_zip.write(readme_path, arcname=os.path.basename(readme_path))

    def move_zips_to_zgames(self):
        print("Moving zips to permanent directory")
        for path in self.to_move:
            try:
                dst = os.path.join(settings.BASE_DIR, "zgames", "mass", os.path.basename(path))
                shutil.move(path, dst)
            except Exception:
                print("Failed to move", src, "to", dst)

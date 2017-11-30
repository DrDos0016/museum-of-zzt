import django
import os
import sys
import zipfile

sys.path.append("/var/projects/museum")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from z2_site.models import File

""" This tool is a one-off and is designed solely for a dev environment """


def main():
    files = File.objects.all().order_by("letter", "title")
    for f in files:
        letter = f.letter
        zip = f.filename

        # Open the zip
        print("==========" * 6)
        print(str(f.id).zfill(4) +
              " [" + letter + "] " + f.filename + " (" + f.title + ")"
              )
        try:
            zip = zipfile.ZipFile(
                "/var/projects/museum/zgames/" + letter + "/" + zip
            )
        except Exception as e:
            print("\t" + str(e))
            continue

        # Print files
        try:
            file_list = zip.namelist()

            for file in file_list:
                print("\t" + file)
        except:
            continue
    return True

if __name__ == "__main__":
    main()

import django
import os
import sys

sys.path.append("/var/projects/museum")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from z2_site.models import File


def main():
    files = File.objects.filter(title__endswith=", The")
    for file in files:
        print(file)
        file.title = "The " + file.title[:-5]
        print("\t", file.title)
        file.save()
    return True

if __name__ == "__main__":
    main()

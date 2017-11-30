import django
import os
import sys

sys.path.append("/var/projects/museum")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from z2_site.models import File


def main():
    for file in File.objects.all():
        print(file)
        file.save()
    return True

if __name__ == "__main__":
    main()

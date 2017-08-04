import django, sys, os, json

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import *

def main():
    """
    This calls .save() on every File object.
    """
    for f in File.objects.all():
        try:
            f.save()
        except:
            print("Couldn't save", f)

    return True

if __name__ == "__main__":main()

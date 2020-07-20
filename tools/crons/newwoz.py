import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

print("NEW WOZZT TEST")

from museum_site.wozzt_queue import WoZZT_Queue  # noqa: E402


def main():
    entry = WoZZT_Queue.objects.all().order_by("-priority", "id")[0]

    entry.send_tweet()
    entry.delete_image()
    entry.delete()
    print("Well that was easy.")


if __name__ == "__main__":
    main()

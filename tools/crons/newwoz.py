import os

import django

from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.wozzt_queue import WoZZT_Queue  # noqa: E402


def main():
    now = datetime.now()

    if now.weekday() == 1:  # Tuesday
        entry = WoZZT_Queue.objects.filter(category="tuesday")
    else:
        entry = WoZZT_Queue.objects.filter(category="wozzt")

    entry = entry.order_by("-priority", "id")[0]
    entry.send_tweet()
    entry.delete_image()
    entry.delete()
    print("Done.")


if __name__ == "__main__":
    main()

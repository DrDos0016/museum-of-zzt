import os
import django

from datetime import datetime

django.setup()

from museum_site.models.wozzt_queue import WoZZT_Queue  # noqa: E402


def main():
    SERVICES = ["tumblr", "mastodon", "discord", "bluesky"]
    now = datetime.now()
    category = "tuesday" if now.weekday() == 1 else "wozzt"
    entry = WoZZT_Queue.objects.filter(category=category).order_by("-priority", "id")[0]

    # Send everywhere
    for s_name in SERVICES:
        try:
            getattr(entry, "send_{}".format(s_name))()
        except:
            print("Failed to send: " + s_name)

    # Delete when done
    entry.delete_image()
    entry.delete()
    print("Done.")


if __name__ == "__main__":
    main()

import os

import django

from datetime import datetime

django.setup()

from museum_site.models.wozzt_queue import WoZZT_Queue  # noqa: E402


def main():
    now = datetime.now()

    if now.weekday() == 1:  # Tuesday
        entry = WoZZT_Queue.objects.filter(category="tuesday")
    else:
        entry = WoZZT_Queue.objects.filter(category="wozzt")

    entry = entry.order_by("-priority", "id")[0]

    # Send everywhere
    try:
        entry.send_tumblr()
    except:
        print("Failed to send: Tumblr")

    try:
        entry.send_mastodon()
        entry.send_discord()
    except:
        print("Failed to send: Mastodon and/or Discord")

    try:
        entry.send_tweet()
    except:
        print("Failed to send: Twitter")

    try:
        entry.send_chost()
    except:
        print("Failed to send: Cohost")

    # Delete
    entry.delete_image()
    entry.delete()
    print("Done.")


if __name__ == "__main__":
    main()

import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    to_remove = [
        '<a href="https://www.youtube.com/channel/UCr0f-r1bRexAZK8sWyk4NJA" target="_blank">Worlds of ZZT on YouTube</a><br>',
        '<a href="https://twitch.tv/worldsofzzt" target="_blank">Worlds of ZZT on Twitch</a>',
        '<a href="https://www.youtube.com/channel/UCr0f-r1bRexAZK8sWyk4NJA">Worlds of ZZT on YouTube</a>',
        '<a href="https://twitch.tv/worldsofzzt">Worlds of ZZT on Twitch</a>',
        '<!-- CONTENT END -->',
    ]

    print("Remove links to youtube/twitch from Livestream articles")
    input("Press Enter to begin. This will impact the database.")
    qs = Article.objects.filter(category="livestream").order_by("id")
    for a in qs:
        size = len(a.content)
        for remove in to_remove:
            a.content = a.content.replace(remove, "")
        new_size = len(a.content)
        a.content = a.content.strip()
        if new_size != size:
            print("ADJUSTED", a)
        a.save()
    return True


if __name__ == '__main__':
    main()

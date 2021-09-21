import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402

CHANGES = [
    {"pk": 349, "lang": "nl", "etc": "Dutch Coll."},
    {"pk": 350, "lang": "nl", "etc": "Dutch Coll. 2"},
    {"pk": 267, "lang": "nl", "etc": "Dutch Coll. 3"},
    {"pk": 2126, "lang": "es", "etc": "Epic"},
    {"pk": 3291, "lang": "it", "etc": "Fortress of ZZT [it]"},
    {"pk": 2477, "lang": "fr", "etc": "General Anger"},
    {"pk": 2599, "lang": "nl", "etc": "Het Grote Vakantieman Avontuur"},
    {"pk": 1579, "lang": "da", "etc": "I fængsel"},
    {"pk": 2684, "lang": "de", "etc": "Labyrinth ZZT 3"},
    {"pk": 2600, "lang": "nl", "etc": "Life of a Scotter - Nederlandse versie"},
    {"pk": 2682, "lang": "de", "etc": "Mathias Aegler's ZZT"},
    {"pk": 2683, "lang": "de", "etc": "Mathias Aegler's ZZT 2"},
    {"pk": 3294, "lang": "no", "etc": "Prison [no]"},
    {"pk": 2156, "lang": "da", "etc": "Prisoner"},
    {"pk": 3101, "lang": "es", "etc": "SaintZZT 13th"},
    {"pk": 2601, "lang": "nl", "etc": "TNMP Megapack 1"},
    {"pk": 2602, "lang": "nl", "etc": "TNMP Megapack 2"},
    {"pk": 3256, "lang": "no", "etc": "Tormod sin verden!! [no]"},
    {"pk": 2076, "lang": "xx", "etc": "Yiepipipi"},
    {"pk": 2367, "lang": "en/es", "etc": "SaintZZT 1st"},
    {"pk": 1180, "lang": "en/es", "etc": "SaintZZT 4th"},
    {"pk": 1023, "lang": "es", "etc": "SaintZZT 5th"},
    {"pk": 1024, "lang": "en/es", "etc": "SaintZZT 7th"},
    {"pk": 2533, "lang": "en/es", "etc": "SaintZZT 7th 1999-11-09"},
    {"pk": 1182, "lang": "en/es", "etc": "SaintZZT 7th Enhanced"},
    {"pk": 2368, "lang": "en/es", "etc": "SaintZZT 8th"},
    {"pk": 2365, "lang": "es", "etc": "SaintZZT 10th"},
    {"pk": 2366, "lang": "es", "etc": "SaintZZT 11th"},
    {"pk": 3101, "lang": "es", "etc": "SaintZZT 13th"},
    #{"pk": 0, "lang": "", "etc": ""},
]



def main():
    print("This script will change the language field for games that are "
          "non-English.")

    input("Enter to apply changes. ")

    for c in CHANGES:
        f = File.objects.filter(pk=c["pk"]).first()
        if not f:
            print("COULD NOT FIND PK", c["pk"])
            continue

        f.language = c["lang"]
        f.save()

        print("Set language to", c["lang"], "for", str(f))

    return True


if __name__ == '__main__':
    main()

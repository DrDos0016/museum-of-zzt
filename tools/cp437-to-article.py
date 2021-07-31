import codecs
import datetime
import glob
import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import *  # noqa: E402
from museum_site.constants import *  # noqa: E402

# Defaults
AUTHOR = "Various"
CATEGORY = "Historical"
"""http://django.pi:8000/article/historical/"""
INFO = {
    "NL1-04.TXT": {
        "title": "The NL - Issues 1-4",
        "summary": "Inside: ZZT reviews, MZX troubleshooting, MZX Previews, Mission: Enigma Walkthroguh, Petitoning AOL for a ZZT/MZX forum, ASCII Smiley faces, and more",
        "date": datetime.date(year=1970, month=1, day=1),
    },
    "NLV2_01.TXT": {
        "title": "The NL - Volume 2 Issue 1",
        "summary": "Inside: HOTwired, The Good The Bad and the Yellow Bordered, MZX Previews, Mission: Enigma Walkthrough",
        "date": datetime.date(year=1970, month=1, day=1),
    },
    "NLV2_02.TXT": {
        "title": "The NL - Volume 2 Issue 2",
        "summary": "Inside: Chris Part 2 Walkthrough, Ultraware Previews, The Critic Corner, The Good The Bad and the Yellow-Bordered",
        "date": datetime.date(year=1970, month=1, day=1),
    },
    "NLV2_03.TXT": {
        "title": "The NL - Volume 2 Issue 3 (The Issue for Windows)",
        "summary": "Inside: Sez Me, The Critic Corner, The School Blues, The Good The Bad and the Yellow-Bordered",
        "date": datetime.date(year=1995, month=10, day=31),
    },
    "NLV2_04.TXT": {
        "title": "The NL - Volume 2 Issues 4 (The Thanksgiving and Christmas Special)",
        "summary": "Inside: NL NeWz, The Critic Corner",
        "date": datetime.date(year=1995, month=12, day=31),
    },
    "NLV3_01.TXT": {
        "title": "The NL - Volume 3 Issue 1 (The happy NL Year issue)",
        "summary": "Inside: HOTwired, Company Drama, Alexis Janson Profile, The Critic Corner",
        "date": datetime.date(year=1996, month=1, day=31),
    },
    "NLV3_02.TXT": {
        "title": "The NL - Volume 3 Issue 2 (The Unavailing Issue)",
        "summary": "Inside: Alexis Jason Retires From ZZT, Games To Look Out For, About Link's Chaotic Adventure, ZZT and MZX News Monthly, NL NeWz, The Critic Corner",
        "date": datetime.date(year=1996, month=1, day=31),
    },
    "NLV3_03.TXT": {
        "title": "The NL - Volume 3 Issue 3 (The Mega-PACKED Issue)",
        "summary": "Inside: Coolness preview, Outpost Software Business Updates, White Tiger Software Updates, NL NeWz, HOTwired, CRiTiqueX MZX, MZX Cranky Kong Korner",
        "date": datetime.date(year=1996, month=3, day=31),
    },
    "Nlv3_04.txt": {
        "title": "The NL - Volume 3 Issue 4 (Use to be the April Fool's Issue)",
        "summary": "Inside: White Tiger Column, Hyperware News, NL NeWz - Top Ten Design Sins, Company Updates, CRiTiqueX MZX, The Critic Corner MZX ",
        "date": datetime.date(year=1996, month=4, day=30),
    },
    "NLV3_05.TXT": {
        "title": "The NL - Volume 3 Issue 5 (The May Issue)",
        "summary": "Inside: Really Kewl Stuff, How to tell if you're a good ZZT game maker, NL NeWz, AOL Upload Troubles",
        "date": datetime.date(year=1996, month=5, day=31),
    },
    "NLV3_06.TXT": {
        "title": "The NL - Volume 3 Issue 6 (The Issue to Summer Vacation)",
        "summary": "Inside: The Tiger's Den, ICE! Preview, The Critic Corner, ",
        "date": datetime.date(year=1996, month=6, day=30),
    },
    "NLV3_07.TXT": {
        "title": "The NL - Volume 3 Issue 7 (The Dull Issue)",
        "summary": "Inside: The Tiger's Den, A new ZZT/MZX CLone FoxEY, The Critic Corner",
        "date": datetime.date(year=1996, month=7, day=31),
    },
    "NLV3_08.TXT": {
        "title": "The NL - Volume 3 Issue 8 (The Summer Wrap-Up Issue)",
        "summary": "Inside: NL NeWz, MZXSpace Award Winners, Time Tech Foundation Update, NL Changes, The Critic Corner",
        "date": datetime.date(year=1996, month=8, day=31),
    },
    "NLV3_09.TXT": {
        "title": "The NL - Volume 3 Issue 9 (The School's Back Issue)",
        "summary": "Inside: NL Column About Nothing In Particular, Matt Williams Interview, The Tiger's Lair, AOL 3.0 Windows 3.1 vs Windows 95 Beta, The Critic Corner",
        "date": datetime.date(year=1996, month=9, day=30),
    },
    "NLV3_10.TXT": {
        "title": "The NL - Volume 3 Issue 10 (The Double Issue (Not.))",
        "summary": "Inside: NL NeWz, The NL Column About Nothing In Particular, The Critic Corner, Other News",
        "date": datetime.date(year=1996, month=11, day=30),
    },
    "NLV3_11.TXT": {
        "title": "The NL - Volume 3 Issue 11 (The Christmas Issue)",
        "summary": "Inside: MZX'ed, ZPlayer's Ads, NORMAL? PRoDuCTioNS Previews, The ZOP Stop, The Critic Corner",
        "date": datetime.date(year=1996, month=12, day=31),
    },
    "Nlv4_04.txt": {
        "title": "The NL - Volume 4 Issue 4 (The Spring Issue)",
        "summary": "Inside: Rants, Yet Another NL Column About Nothing In Particular, The Critic's Corner",
        "date": datetime.date(year=1997, month=4, day=30),
    },
    "Nlv5_01.txt": {
        "title": "The NL - Volume 5 Issue 1 (From the Ashes)",
        "summary": "Inside: Letters from the Predator",
        "date": datetime.date(year=1970, month=1, day=1),
    },
}

def main():
    print("Press Enter to continue")
    files = glob.glob(os.path.join("data", "cp437files", "*"))
    sorted(files)

    for f in files:
        print(f)
        if os.path.basename(f) == "NlNeWz10.txt":
            continue

        with codecs.open(f, encoding="cp437") as fh:
            text = fh.read()

        with codecs.open("CONV.TXT", "w", encoding="utf8") as fh:
            fh.write(text)

        with codecs.open("CONV.TXT", encoding="utf8") as fh:
            content = fh.read()

        print("Creating article...")
        a = Article()
        a.title = INFO[os.path.basename(f)]["title"]
        a.author = AUTHOR
        a.category = CATEGORY
        a.content = content
        a.publish_date = INFO[os.path.basename(f)]["date"]
        a.schema = "80col"
        a.published = PUBLISHED_ARTICLE
        a.summary = INFO[os.path.basename(f)]["summary"]
        a.allow_comments = True
        a.spotlight = False
        a.static_directory = "the-nl"
        a.save()
        print("Saved!", a.id)

    return True

    os.remove("CONV.TXT")

if __name__ == '__main__':
    main()

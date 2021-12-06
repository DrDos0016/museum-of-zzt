import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402

PURPOSE = """
Running this script will create Series objects in the database and then adjust
articles to associate them with those series.
"""

SERIES_INFO = [
    {
        "title": "Epic MegaGames Documents",
        "description": (
            "Official documents relating to ZZT. These include manuals, hint \
            sheets, full walkthroughs, advertisements, newsletters, and \
            company documents"
        ),
        "visible": True,
        "article_ids": [
            265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 445, 515, 518
        ],
    },
    {
        "title": "NextGame 33 Closer Look",
        "description": (
            "Closer Looks covering \"NextGame 33\""
        ),
        "visible": True,
        "article_ids": [282, 283],
    },
    {
        "title": "Operation Gamma Velorum Livestream",
        "description": (
            "Livestreams covering the \"Operation Gamma Velorum\" \
            series"
        ),
        "visible": True,
        "article_ids": [384, 385, 387, 388],
    },
    {
        "title": "For Elise Livestream",
        "description": (
            "Livestreams covering a complete playthrough of \"For Elise\""
        ),
        "visible": True,
        "article_ids": [423, 426, 427],
    },
    {
        "title": "Yuki and the Space Show Livestream",
        "description": (
            "Livestreams covering a complete playthrough of \"Yuki and the \
            Space Show\""
        ),
        "visible": True,
        "article_ids": [429, 430],
    },
    {
        "title": "Super Archaeologist Simulator Livestream",
        "description": (
            "Livestreams covering a complete playthrough of \"Super \
            Archaeologist Simulator\""
        ),
        "visible": True,
        "article_ids": [434, 435],
    },
    {
        "title": "November Eve Closer Look",
        "description": (
            "Closer Looks covering \"November Eve\""
        ),
        "visible": True,
        "article_ids": [436, 443],
    },
    {
        "title": "The Joy of ZZT",
        "description": (
            "Livestreams which showcase how to create your own ZZT worlds \
            using the KevEdit editor. This video tutorial is intended for \
            beginners, starting from a fresh install of ZZT, Zeta, and \
            KevEdit. It covers basic ZZT elements, ZZT-OOP programming, \
            developing an engine, and general ZZT game design tips"
        ),
        "visible": True,
        "article_ids": [453, 454, 455, 456, 457, 460, 463, 465, 469, 477],
    },
    {
        "title": "Secret Agent Joe Moe Livestream",
        "description": (
            "Livestreams covering a complete playthrough of \"Secret Agent \
            Joe Moe\""
        ),
        "visible": True,
        "article_ids": [472, 473],
    },
    {
        "title": "Invasion ZZT Revision Closer Look",
        "description": (
            "Closer Looks covering \"Invasion ZZT Revision\""
        ),
        "visible": True,
        "article_ids": [480, 484],
    },
    {
        "title": "Dark Citadel Livestream",
        "description": (
            "Livestreams covering a complete playthrough of \"Dark Citadel\""
        ),
        "visible": True,
        "article_ids": [497, 498],
    },
    {
        "title": "Oktrollberfest 2020 Livestream",
        "description": (
            "Livestreams covering Dr. Dos's playthrough of the worlds \
            submitted to the Oktrollberfest 2020 game jam and the awards \
            ceremony streams hosted by WiL and KKairos"
        ),
        "visible": True,
        "article_ids": [504, 505, 508],
    },
    {
        "title": "Invasion ZZT Revision Livestream",
        "description": (
            "Livestreams covering a complete playthrough of \"Invasion ZZT \
            Revision\""
        ),
        "visible": True,
        "article_ids": [506, 509],
    },
    {
        "title": "ZZT 30th Anniversary Livestream",
        "description": (
            "A celebration of ZZT turning 30 on January 15th, 2021. This \
            series consists of livestreams for the original four ZZT worlds \
            as well as a playthrough of \"Town of ZZT Remix\" released at the \
            start of the year."
        ),
        "visible": True,
        "article_ids": [513, 514, 516, 517, 522, 523, 527],
    },
    {
        "title": "ZZT GAMES IMPORTANT!",
        "description": (
            "A playthrough of a few unpreserved ZZT worlds from the early \
            90s recovered off of a donated 5.25\" floppy disk."
        ),
        "visible": True,
        "article_ids": [543, 544],
    },
    {
        "title": "Chrono Wars Chronology",
        "description": (
            "Livestreams covering a complete playthrough of the \"Chrono \
            Wars\" series. All thirteen games and an article comparing \
            various revisions of the games."
        ),
        "visible": True,
        "article_ids": [545, 552, 556, 562, 565, 577, 581, 583, 605, 616],
    },
    {
        "title": "Overflow Closer Look",
        "description": (
            "Closer Looks covering \"Overflow\""
        ),
        "visible": True,
        "article_ids": [554, 560],
    },
    {
        "title": "Best of ZZT",
        "description": (
            "A series consisting of recommendations for notable ZZT worlds \
            throughout the years"
        ),
        "visible": True,
        "article_ids": [295, 563],
    },
    {
        "title": "Big Leap Livestream",
        "description": (
            "Livestreams covering a complete playthrough of \"The Big Leap\""
        ),
        "visible": True,
        "article_ids": [569, 572],
    },
    {
        "title": "Landland Closer Look",
        "description": (
            "Closer Looks covering both games in the \"Landland\" series"
        ),
        "visible": True,
        "article_ids": [567, 573],
    },
    {
        "title": "When East Met West: The Pact of Steel Livestream",
        "description": (
            "Livestreams covering a complete playthrough of \"When East Met \
            West: The Pact of Steel\""
        ),
        "visible": True,
        "article_ids": [582, 584],
    },
    {
        "title": "NL",
        "description": (
            "A collection of issues of a ZZT/MZX newsletter known as \"The \
            NL\" filled with then contemporary reviews, previews, and other \
            insights into the ZZT/MZX communities of the era"
        ),
        "visible": True,
        "article_ids": [
            585, 594, 593, 595, 591, 598, 600, 597, 590, 601, 603, 602, 592,
            587, 586, 588, 589, 596, 599
        ],
    },
    {
        "title": "Rhygar 2 Livestream",
        "description": (
            "Livestreams covering a complete playthrough of \"Rhygar 2\""
        ),
        "visible": True,
        "article_ids": [606, 610],
    },
    {
        "title": "Phoebus Project Livestream",
        "description": (
            "Livestreams covering a complete playthrough of \"Phoebus \
            Project\". This does not include the separately released epilogue."
        ),
        "visible": True,
        "article_ids": [613, 617],
    },
    {
        "title": "War-Torn Livestream",
        "description": (
            "Livestreams covering a complete playthrough of \"War-Torn\" and \
            the demo for its sequel \"Runied World\""
        ),
        "visible": True,
        "article_ids": [626, 629],
    },
    {
        "title": "Oktrollberfest 2021 Livestream",
        "description": (
            "Livestreams covering a Dr. Dos's playthrough of the ZZT worlds \
            and one non-ZZT world submitted to the Oktrollberfest 2021 game \
            jam"
        ),
        "visible": True,
        "article_ids": [643, 644, 646, 647],
    },
    {
        "title": "Tyrobain Livestream",
        "description": (
            "Livestreams covering a complete playthrough of \"Tyrobain\""
        ),
        "visible": True,
        "article_ids": [649, 652],
    },
]


def main():
    print(PURPOSE)
    input("Press Enter to begin")

    for i in SERIES_INFO:
        s = Series(
            title=i["title"],
            description=i["description"],
            visible=i["visible"]
        )

        s.save()
        print("Created series:", s.title)

        for pk in i["article_ids"]:
            try:
                a = Article.objects.get(pk=pk)
                a.series.add(s)
                a.save()
                print(" - " + a.title)
            except Exception:
                print(" - NO ARTICLE FOUND WITH ID", pk)

    print("DONE.")
    return True


if __name__ == '__main__':
    main()

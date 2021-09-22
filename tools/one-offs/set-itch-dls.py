import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402

CHANGES = [
    #{"pk": 0, "lang": "", "etc": ""},
    {"pk": 2846, "url": "https://dr-dos.itch.io/the-mars-rover"},
    {"pk": 2863, "url": "https://dr-dos.itch.io/upsidetown"},
    {"pk": 2880, "url": "https://dr-dos.itch.io/wake-up-and-save-the-world"},
    {"pk": 3150, "url": "https://dr-dos.itch.io/doug-tudeap-in-the-ore-gone-trail"},
    {"pk": 2547, "url": "https://jdmgames.itch.io/nibblin"},
    {"pk": 3248, "url": "https://pogesoft.itch.io/587-squadron-advance"},
    {"pk": 3089, "url": "https://stale-meme-emporium.itch.io/kunger-binb-1"},
    {"pk": 2424, "url": "https://farawaytimes.itch.io/atop-the-witchs-tower"},
    {"pk": 2867, "url": "https://stale-meme-emporium.itch.io/the-king-in-yellow-borders"},
    {"pk": 3259, "url": "https://pogesoft.itch.io/587-squadron"},
    {"pk": 3230, "url": "https://pogesoft.itch.io/587-squadron"},
    {"pk": 2628, "url": "https://kkairos.itch.io/cdslash"},
    {"pk": 2828, "url": "https://kkairos.itch.io/cdslash"},
    {"pk": 2604, "url": "https://emmzee.itch.io/daedalus-obelisk-zzt"},
    {"pk": 2876, "url": "https://zephyr2525.itch.io/on-a-distant-moon"},
    {"pk": 2878, "url": "https://stale-meme-emporium.itch.io/bubbas-bubbles"},
    {"pk": 2441, "url": "https://rabbitboots.itch.io/faux-amis-zzt"},
    {"pk": 2442, "url": "https://rabbitboots.itch.io/faux-amis-zzt"},
    {"pk": 2443, "url": "https://rabbitboots.itch.io/faux-amis-zzt"},
    {"pk": 2622, "url": "https://rabbitboots.itch.io/faux-amis-zzt"},
    {"pk": 2594, "url": "https://kkairos.itch.io/kerfuffle"},
    {"pk": 2866, "url": "https://kkairos.itch.io/big-beast-in-the-maze"},
    {"pk": 3128, "url": "https://kkairos.itch.io/big-beast-in-the-maze"},
    {"pk": 2883, "url": "https://zephyr2525.itch.io/ramen-quest"},
    {"pk": 2879, "url": "https://pogesoft.itch.io/toucanchevskys-starling"},
    {"pk": 2943, "url": "https://pogesoft.itch.io/metal-saviour-bia"},
    {"pk": 2980, "url": "https://pogesoft.itch.io/metal-saviour-bia"},
    {"pk": 2882, "url": "https://studiodraconis.itch.io/potion-notions"},
    {"pk": 2938, "url": "https://zephyr2525.itch.io/burger-digital-holiday-special"},
    {"pk": 2950, "url": "https://kkairos.itch.io/magi"},
    {"pk": 2958, "url": "https://verasev.itch.io/mutant-citadel"},
    {"pk": 2976, "url": "https://verasev.itch.io/mutant-citadel"},
    {"pk": 2426, "url": "https://rabbitboots.itch.io/maze-minders-bitsy-to-zzt-conversion"},
    {"pk": 2799, "url": "https://stale-meme-emporium.itch.io/variety"},
    #{"pk": 0, "url": "https://stale-meme-emporium.itch.io/nautilus-early-access-demo"},
    {"pk": 2887, "url": "https://zinfandelzt.itch.io/uriah-madborogh"},
    {"pk": 2756, "url": "https://pogesoft.itch.io/the-quest-for-coffee"},
    {"pk": 2290, "url": "https://pogesoft.itch.io/the-quest-for-coffee"},
    {"pk": 2886, "url": "https://meangirls.itch.io/kitten-hallway"},
    {"pk": 3236, "url": "https://stale-meme-emporium.itch.io/when-there-is-no-more-maze"},
    #{"pk": 0, "url": "https://pogesoft.itch.io/heimweh-demo"},
    {"pk": 3100, "url": "https://pogesoft.itch.io/davidbeast-wrestler"},
    {"pk": 3194, "url": "https://pogesoft.itch.io/no-szzt"},
    {"pk": 3151, "url": "https://whydoisay.itch.io/when-there-is-no-more-snow"},
    {"pk": 3007, "url": "https://electrum-glitches.itch.io/slumberpocalypse"},
    {"pk": 2625, "url": "https://zephyr2525.itch.io/yuki-and-the-space-show"},
]


def main():
    print("This script will add download URLs for known Itch games.")
    print("Do not run multiple times as this will create duplicate download")
    print("objects.")
    input("Enter to apply changes. ")

    for c in CHANGES:
        f = File.objects.filter(pk=c["pk"]).first()
        if not f:
            print("COULD NOT FIND PK", c["pk"])
            continue

        d = Download(url=c["url"], kind="itch")
        d.save()

        f.downloads.add(d)

        print("Added download for", str(f))

    return True


if __name__ == '__main__':
    main()

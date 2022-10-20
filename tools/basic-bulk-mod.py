import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402

URLS = """
https://museumofzzt.com/file/view/zeldagam/
https://museumofzzt.com/file/view/tlozdemo/
https://museumofzzt.com/file/view/z1hero/
https://museumofzzt.com/file/view/zelda2dem/
https://museumofzzt.com/file/view/legendofzelda1/
https://museumofzzt.com/file/view/legendofzelda2/
https://museumofzzt.com/file/view/legendofzelda3/
https://museumofzzt.com/file/view/zelda2dm/
https://museumofzzt.com/file/view/zeldalordofguardia/
https://museumofzzt.com/file/view/mario64/
https://museumofzzt.com/file/view/mario1/
https://museumofzzt.com/file/view/mariobr1/
https://museumofzzt.com/file/view/mario2/
https://museumofzzt.com/file/view/mariopca/
https://museumofzzt.com/file/view/mariorpg/
https://museumofzzt.com/file/view/smario1/
https://museumofzzt.com/file/view/marioss/
https://museumofzzt.com/file/view/marioyoshiandboshiv3/
https://museumofzzt.com/file/view/linktgy1/
https://museumofzzt.com/file/view/linkadv1/
https://museumofzzt.com/file/view/linkadv2/
https://museumofzzt.com/file/view/linkadv3/
https://museumofzzt.com/file/view/pokemonzzz/
https://museumofzzt.com/file/view/pmd-z/
https://museumofzzt.com/file/view/ppart1/
https://museumofzzt.com/file/view/pokepak/
https://museumofzzt.com/file/view/pkmult1/
https://museumofzzt.com/file/view/pkmn-fm/
https://museumofzzt.com/file/view/stbc00001b/
https://museumofzzt.com/file/view/stbc00003a/
https://museumofzzt.com/file/view/search/
https://museumofzzt.com/file/view/sw/
https://museumofzzt.com/file/view/swevii/
https://museumofzzt.com/file/view/swepviidem/
https://museumofzzt.com/file/view/cswdemo/
https://museumofzzt.com/file/view/heir2emp/
https://museumofzzt.com/file/view/frandori/
https://museumofzzt.com/file/view/saveleia/
https://museumofzzt.com/file/view/sonicrevised/
https://museumofzzt.com/file/view/sazzt/
https://museumofzzt.com/file/view/hedgehog/
https://museumofzzt.com/file/view/sonic1d/
https://museumofzzt.com/file/view/soniczzt/
https://museumofzzt.com/file/view/sonic_b/
https://museumofzzt.com/file/view/mmzzt/
https://museumofzzt.com/file/view/digichar/
https://museumofzzt.com/file/view/mbmtpr/
https://museumofzzt.com/file/view/mmpdstr/
https://museumofzzt.com/file/view/smpr/
https://museumofzzt.com/file/view/smpr0402/
https://museumofzzt.com/file/view/wwfkotr/
"""


def main():
    g = Genre.objects.get(title="Fangame")
    raw = URLS.split("\n")
    for url in raw:
        if not url:
            continue
        url = url.replace("https://museumofzzt.com/file/view/", "")
        key = url.replace("/", "")
        zf = File.objects.get(key=key)
        zf.genres.add(g)
        zf.basic_save()
    return True


if __name__ == '__main__':
    main()

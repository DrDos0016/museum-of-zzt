import glob
import os
import subprocess
import sys
import urllib.request
import zipfile

import django

sys.path.append("/var/projects/museum")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import File

import zookeeper

urls = [
"https://museumofzzt.com/file/d/duke.zip?file=DUKE.ZZT&board=5",
"https://museumofzzt.com/file/j/jack-o-l.zip?file=Jack-o-l.zzt&board=9",
"1999",
"https://museumofzzt.com/file/j/jamijo.zip?file=Jamijo.zzt&board=6",
"2000",
"https://museumofzzt.com/file/i/indreams.zip?file=INDREAMS.ZZT&board=4",
"https://museumofzzt.com/file/d/drwho1.zip?file=WHO-SE.ZZT&board=13",
"https://museumofzzt.com/file/k/kave-se.zip?file=KAVE-SE.ZZT&board=1",
"2001",
"https://museumofzzt.com/file/g/gh2se.zip?file=Gh2-se.zzt&board=22",
"https://museumofzzt.com/file/d/decguida.zip?file=DECGUID1.ZZT&board=18",
"https://museumofzzt.com/file/s/Srpggggg.zip?file=SRPGGGGG.ZZT&board=2",
"https://museumofzzt.com/file/1/four.zip?file=4.ZZT&board=3",
"https://museumofzzt.com/file/1/four.zip?file=4.ZZT&board=4",
"2002",
"https://museumofzzt.com/file/c/comxmas.zip?file=COMXMAS1.ZZT&board=1",
"https://museumofzzt.com/file/c/comxmas.zip?file=COMXMAS1.ZZT&board=4",
"https://museumofzzt.com/file/v/V302SE.zip?file=V302SE.ZZT&board=2",
"https://museumofzzt.com/file/v/vegetakeover.zip?file=VEGE1.ZZT&board=8",
"https://museumofzzt.com/file/s/simlife.zip?file=SIMLIFE.ZZT&board=8",
"https://museumofzzt.com/file/l/livedead.zip?file=LIVEDEAD.ZZT&board=11",
"https://museumofzzt.com/file/l/livedead.zip?file=LIVEDEAD.ZZT&board=12",
"https://museumofzzt.com/file/b/burglar!.zip?file=burglar1.zzt&board=12",
"https://museumofzzt.com/file/b/burglar!.zip?file=burglar1.zzt&board=13",
"https://museumofzzt.com/file/b/burglar!.zip?file=burglar1.zzt&board=23",
"https://museumofzzt.com/file/f/ffdisc1.zip?file=FFDISC1.ZZT&board=11",
"https://museumofzzt.com/file/s/Scarlet.zip?file=SCARLET.ZZT&board=1",
"2003",
"https://museumofzzt.com/file/e/Esp.zip?file=ESPFILE4.ZZT&board=30",
"https://museumofzzt.com/file/s/Smashed.zip?file=SMASHED.ZZT&board=7",
"https://museumofzzt.com/file/f/frost1.zip?file=FROST1.ZZT&board=30",
"2007",
"https://museumofzzt.com/file/f/Frost2.zip?file=FROST2.ZZT&board=6",
"https://museumofzzt.com/file/f/Frost2.zip?file=FROST2.ZZT&board=9",
"https://museumofzzt.com/file/f/Frost2.zip?file=FROST2.ZZT&board=11",
"2008",
"https://museumofzzt.com/file/p/PARROTY.zip?file=PARROTY.ZZT&board=10",
"https://museumofzzt.com/file/e/elis_h_1.1.zip?file=elis_h_1.zzt&board=6",
"https://museumofzzt.com/file/a/Algorithm.zip?file=ALGORITH.ZZT&board=6",
"2009",
"https://museumofzzt.com/file/r/ROBOTS2.zip?file=ROBOTS2.ZZT&board=4",
"https://museumofzzt.com/file/c/CATCAT.zip?file=CATCAT.ZZT&board=5",
"https://museumofzzt.com/file/c/CATCAT.zip?file=CATCAT.ZZT&board=10",
"2010",
"https://museumofzzt.com/file/q/quiet1.zip?file=quiet1.zzt&board=2",
"2011",
"https://museumofzzt.com/file/k/kramer.zip?file=KRAMER.ZZT&board=1",
"2015",
"https://museumofzzt.com/file/a/ADVLINK2.ZIP?file=advlink2.zzt&board=3",

]

template = '<b>{}</b> as seen in <a href="{}" target="_blank">{}</a>\n<img class="c" src="XX static \'images/articles/cl/houses/{}.png\' XY">\n'

for url in urls:

    if url[0] != "h":
        print("<h2>" + url + "</h2>\n")
        continue

    letter = url[29]
    zipname = url[31:].split("?")[0]
    zztname = url.split("=")[1].split("&")[0]
    board = url.split("=")[2]

    # Get the file info
    #print(letter, zipname)
    f = File.objects.get(letter=letter, filename=zipname)

    #print(letter, zipname, zztname, board)

    # Get the zip
    z = zipfile.ZipFile("/var/projects/museum/zgames/" + letter + "/" + zipname)

    z.extract(zztname)
    z = zookeeper.Zookeeper(zztname)
    board_name = z.boards[int(board)].title

    print(template.format(board_name, url, f.title, zztname[:-4]).replace("XX", "{%").replace("XY", "%}"))


# "https://museumofzzt.com/file/p/pupegold.zip?file=PGOLDEXP.ZZT&board=2",
# "https://museumofzzt.com/file/w/wongroom.zip?file=WONGROOM.ZZT&board=1",

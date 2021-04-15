import glob
import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import *  # noqa: E402

STATIC_DIRS = {
    "1": "About-zzt",
    "2": "Zzt-versions",
    "3": "Ascii-character-reference",
    "4": "Asbestos-part-one-walkthrough",
    "5": "Getting-started-with-zzt",
    "6": "Zzt-clones",
    "8": "Custom-fonts-and-blinkx",
    "9": "Aura-walkthrough",
    "10": "Zzt-cliches",
    "13": "Helios-board-logs",
    "14": "World-editor-help",
    "22": "Zzt-cheats",
    "23": "Fg-ezanya",
    "24": "Fg-burglar",
    "25": "Fg-dragon-woods",
    "26": "Fg-edible-vomit",
    "27": "Fg-zzt-syndromes",
    "28": "Fg-the-mercenary",
    "29": "Fg-evil-sorcerors-party",
    "30": "Fg-burger-joint",
    "31": "Fg-kudzu-v21",
    "32": "Fg-run-on-v24",
    "33": "Fg-warlocks-domain",
    "34": "Fg-sivion",
    "35": "Fg-little-square-things",
    "36": "Fg-winter",
    "37": "Fg-ned-the-knight",
    "38": "Fg-legend-of-brandonia",
    "39": "Fg-lebensraum",
    "40": "Fg-banana-quest",
    "41": "Fg-dungeon-masters-gallery",
    "42": "Fg-aura",
    "43": "fg-frost-1-power",
    "44": "Fg-mrwaif",
    "45": "Fg-death",
    "46": "Fg-merbotia",
    "47": "Fg-pepper-bolette-se",
    "48": "Fg-elis-house",
    "49": "Fg-smiley-guy-toxic-terminator",
    "50": "Gotm-burger-joint",
    "51": "Gotm-chrono-wars-9",
    "52": "Gotm-pop",
    "53": "Gotm-ned-the-knight",
    "54": "Gotm-the-draco-experience",
    "55": "Gotm-buck-russel-private-eye",
    "56": "Gotm-fabrication",
    "57": "Gotm-speed-racer-x",
    "58": "Gotm-chrono-wars-11",
    "59": "Gotm-nextgame-33",
    "60": "Gotm-teen-priest-2",
    "61": "Gotm-november-eve",
    "62": "Gotm-fantasy-world-dizzy",
    "63": "Gotm-rippled-flesh",
    "64": "Gotm-treasure-island-dizzy",
    "65": "Gotm-dragon-eye",
    "66": "Gotm-stupid-rpg-disc-2",
    "67": "Gotm-bloodlines-disc-1",
    "68": "Gotm-dark-soul",
    "69": "Gotm-scooter",
    "70": "Gotm-last-momentum",
    "71": "Gotm-life-of-a-player-2",
    "72": "Gotm-a-dwarvish-mead-dream",
    "73": "Gotm-lome",
    "74": "Gotm-rup-pig",
    "75": "Gotm-neo-part-1",
    "76": "Gotm-chickenwire-v15",
    "77": "Gotm-voyage-of-four",
    "78": "Gotm-new-demo",
    "79": "Gotm-within-v19",
    "80": "Gotm-run-on",
    "81": "Gotm-lost-refritos-9",
    "82": "Gotm-4",
    "83": "Gotm-today-is-monday",
    "84": "Gotm-no",
    "85": "Gotm-stupid-rpg-third-flavor",
    "86": "Gotm-anthropoid",
    "87": "Gotm-mega-job",
    "88": "Gotm-thief-3",
    "89": "Gotm-nothing-constructive",
    "90": "Gotm-little-square-things",
    "91": "Gotm-a-community-xmas",
    "92": "Gotm-zem-x",
    "93": "Gotm-slime-line",
    "94": "Gotm-burglar",
    "95": "Gotm-the-mercenary",
    "96": "Gotm-defender-of-castle-sin",
    "97": "Gotm-final-fantasy-extreme",
    "98": "Cgotm-gem-hunter-se-v15",
    "99": "Cgotm-death",
    "100": "Cgotm-daemon-riff",
    "101": "Cgotm-fury-spell",
    "102": "Cgotm-war-torn",
    "103": "Cgotm-compound",
    "104": "Cgotm-kamek",
    "105": "Cgotm-phoenix-reich",
    "106": "Cgotm-overflow",
    "107": "Cgotm-burger-joint",
    "108": "Cgotm-blood-oath",
    "109": "Cgotm-xod",
    "110": "Cgotm-warlock-domain",
    "111": "Cgotm-merbotia",
    "112": "Cgotm-end-of-the-world",
    "113": "Cgotm-gem-hunte",
    "114": "Cgotm-zztris",
    "115": "Cgotm-lost-monkeys",
    "116": "Cgotm-edible-vomit",
    "117": "Cgotm-the-long-voyage",
    "119": "Cgotm-cyberworld",
    "120": "Cgotm-sombrero",
    "121": "Cgotm-freedom",
    "122": "Cgotm-pddv",
    "123": "Cgotm-starship-troopers",
    "124": "Cgotm-mined-out",
    "125": "Cgotm-mystic-blade",
    "126": "Cgotm-kudzu-v21",
    "127": "Cgotm-quest-for-the-immortals",
    "128": "Cgotm-blue-moon",
    "129": "Cgotm-escape-from-planet-red-v20",
    "130": "Cgotm-lebensraum",
    "131": "Cgotm-warlords-temple-beta",
    "132": "Cgotm-corrupt-mind",
    "133": "Cgotm-sivion",
    "134": "Cgotm-the-fools-quest",
    "135": "Cgotm-coolness",
    "136": "Cgotm-you-vs-stupidity-2",
    "137": "Bizanloo-walkthrough",
    "138": "Burger-joint-walkthrough",
    "139": "Chrono-wars-i-xiii-walkthrough",
    "142": "Code-red-walkthrough",
    "143": "Dragon-woods-walkthrough",
    "144": "Edible-vomit-walkthrough",
    "145": "Fantasy-world-dizzy",
    "146": "fred-2-walkthrough",
    "147": "Kings-quest-zzt-walkthrough",
    "148": "Kings-quest-zzt-2-walkthrough",
    "149": "kudzu-v20-walkthrough",
    "150": "Life-of-a-player-walkthrough",
    "151": "Life-of-a-player-2-walkthrough",
    "152": "Ned-the-knight-walkthrough",
    "153": "Pepper-bolette-walkthrough",
    "154": "Pop-walkthrough",
    "155": "Quest-for-glory-zzt-walkthrough",
    "156": "Sim-dd-walkthrough",
    "157": "sim-dd-2-walkthrough",
    "158": "sim-dd-3-walkthrough",
    "159": "Teen-priest-walkthrough",
    "160": "teen-priest-2-walkthrough",
    "161": "Warlock-domain-walkthrough",
    "162": "yvs2-walkthrough",
    "163": "File-details",
    "166": "Dungeons-of-zzt",
    "170": "Zem-and-zem-2",
    "172": "Making-the-ruins-of-zzt",
    "173": "Deep-december",
    "175": "640x360x16",
    "177": "Pop-walkthrough",
    "181": "merbotia",
    "183": "The-lost-monkeys",
    "186": "Cat-cat-that-damn-cat",
    "188": "bugtown",
    "190": "Smiey-guy",
    "192": "mst3k",
    "194": "turmoil",
    "196": "virus-302-special-edition",
    "198": "nightmare",
    "201": "Jim-crawford-interview",
    "202": "frost-1-power",
    "204": "aceland",
    "207": "Zzter-comics",
    "208": "Yapok-sundria",
    "211": "oaktown",
    "214": "doom",
    "215": "burglar",
    "219": "zig",
    "225": "forrester",
    "226": "Edible-vomit",
    "227": "quickhack",
    "228": "Psychic-solar-war-adventure",
    "229": "Pswa-code",
    "230": "City-of-zzt",
    "231": "nightplanet",
    "232": "Kevedit-overview",
    "238": "Mtp-oprgv",
    "239": "Mtp-the-search-for-the-magic-flamingo",
    "240": "Mtp-the-living-dead",
    "241": "Mtp-sids-disaster",
    "242": "Mtp-oprgv-part-3",
    "243": "Mtp-rogue-three",
    "244": "Mtp-rebirth-the-uprising",
    "245": "Mtp-vegetable-takeover-part-two",
    "246": "Mtp-xzr-exile",
    "247": "Mtp-the-kane-project-4",
    "248": "Mtp-esp",
    "249": "Mtp-z-bert",
    "250": "Mtp-nexus-times-arrow",
    "251": "Mtp-village-2",
    "252": "mtp-frost-1-power",
    "253": "Mtp-mind-vomit",
    "254": "Mtp-nevada-bob-1",
    "255": "Mtp-rotten-robots",
    "256": "Mtp-wasteland",
    "257": "mtp-33-more-ways-to-die",
    "258": "Mtp-nexus-futures-end",
    "259": "Mtp-oprgv-part-4",
    "260": "Mtp-dragons-disc-1",
    "261": "Mtp-pandemonium-alpha",
    "262": "Mtp-mrwaif",
    "264": "Mtp-thug-life-2",
    "265": "Epic-megagames-newsletter",
    "266": "Caves-of-zzt-map",
    "267": "City-of-zzt-map",
    "268": "The-crypt-hint-sheet",
    "269": "Darbytown-hint-sheet",
    "270": "Dungeons-of-zzt-map",
    "271": "Ezanya-hint-sheet",
    "272": "Fantasy-hint-sheet",
    "273": "Manor-walkthrough",
    "274": "Smiley-guy-advertisement",
    "275": "Fantasy-world-dizzy",
    "276": "Fg-ana",
    "277": "Flower-of-light",
    "278": "School-zzt",
    "279": "Meet-the-tardigrades",
    "280": "Defender-of-castle-sin",
    "281": "Teen-priest",
    "282": "Nextgame-33",
    "283": "Nextgame-33",
    "284": "sivion",
    "285": "Sewers-of-zzt",
    "286": "Adventure-of-sam",
    "287": "Indiana-jones-solomon",
    "288": "Fg-plankton-undersea-adventure",
    "289": "4",
    "290": "Gem-hunter-se",
    "291": "Ls-the-mercenary",
    "292": "Mr-shapiro-lies",
    "293": "Goldeneye-zzt",
    "294": "Bugs-player-clones",
    "295": "The-best-of-zzt",
    "296": "War-of-zzt",
    "297": "wasteland",
    "298": "Angelis-finale",
    "299": "scooter",
    "300": "aut03-24hoz",
    "301": "Pokemon-twin-pack",
    "302": "Sixteen-easy-pieces-walkthrough",
    "303": "Fg-sixteen-easy-pieces",
    "304": "Caves-of-zzt",
    "305": "Card-prime",
    "306": "houses",
    "307": "Shades-of-gray",
    "308": "ezanya",
    "309": "parallel",
    "310": "Jack-o-lantern",
    "311": "Final-fantasy-2",
    "312": "Beth-daggert-interview",
    "313": "Run-on",
    "314": "Ls-cyberworld",
    "315": "Ls-the-living-dead",
    "316": "Ls-the-simpsons",
    "317": "algorithm",
    "318": "syndromes",
    "319": "Frost-ost",
    "320": "frost-2-ice",
    "321": "Freak-da-cat",
    "323": "Lock-picking",
    "324": "Stupid-rpg",
    "345": "Ls-virus-302",
    "346": "Ls-zzt-engine-showcase",
    "347": "Ls-lost-games",
    "348": "Ls-castle-of-zzt",
    "349": "Ls-end-of-the-world",
    "350": "Ls-crime-ring",
    "351": "Ls-doom",
    "352": "Ls-llama-masters",
    "353": "Ls-monster-zoo",
    "354": "Ls-infestation",
    "355": "Ls-chowder",
    "356": "Ls-atop-the-witchs-towr",
    "357": "Ls-esp",
    "358": "Ls-red-isle",
    "359": "Ls-starbase-zzt",
    "360": "Ls-mission-renaissance",
    "361": "Ls-ned-the-knight",
    "362": "Ls-jack-o-lantern",
    "363": "Ls-legend-of-brandonia",
    "364": "Ls-zzt-christmas-concert",
    "365": "Ls-fantasy",
    "366": "Ls-adversiturtle",
    "368": "Ls-freedom",
    "369": "Ls-links-adventure",
    "370": "Ls-zombinator",
    "371": "Ls-rotten-robots",
    "372": "ls-autumn-2003-24hozzt",
    "373": "Ls-sixteen-easy-pieces",
    "374": "Ls-faux-amis",
    "375": "Ls-color-revival",
    "376": "Ls-curse-of-the-vampires-curse",
    "377": "Ls-barney-hunt",
    "378": "Ls-madf",
    "379": "Ls-magicaland-dizzy",
    "380": "Ls-resident-evil-zzt",
    "381": "Ls-nibblin",
    "382": "ls-spring-1999-24hozzt",
    "383": "Ls-stinky-the-sock-munching-ocelot",
    "384": "Ls-oprgv-1",
    "385": "Ls-oprgv-2",
    "386": "Ls-the-lost-monkeys",
    "387": "Ls-oprgv-3",
    "388": "Ls-oprgv-4",
    "389": "Ls-george-badluck",
    "390": "Ls-toxic-terminator",
    "391": "Ls-darbytown",
    "392": "Ls-kerfuffle",
    "393": "Nevada-bob",
    "394": "Ls-daedalus-obelisk",
    "395": "Fg-evilstania",
    "396": "Ls-escape-from-castle-zazoomda",
    "397": "Ls-lost-forest",
    "398": "Forests-laughter",
    "399": "zeta",
    "400": "Ls-sailor-moon-destroyer",
    "401": "Ls-caves-of-fury",
    "402": "The-cliff",
    "403": "Ls-final-quest-of-fury",
    "404": "Warlords-temple",
    "405": "fred1",
    "406": "ls-frost-1-power",
    "407": "Ls-cat-cat",
    "408": "Ls-merbotia",
    "409": "Ls-ana",
    "410": "Cannibal-isle",
    "411": "Ls-robots-of-gemrule",
    "412": "Koopo-the-lemming",
    "413": "Ls-the-magic-cave",
    "414": "Koopo-the-lemming",
    "415": "Ls-keeshs-quest",
    "416": "Ls-keeshs-quest-2",
    "417": "dbz",
    "418": "The-search-for-the-magic-flamingo",
    "419": "Ls-november-eve",
    "420": "Ls-treasure-island-dizzy",
    "421": "Ls-guinea-pig",
    "422": "Zztv-3",
    "423": "Ls-for-elise",
    "424": "Witchs-tower",
    "425": "Dwarvish-mead",
    "426": "Ls-for-elise-part-2",
    "427": "Ls-for-elise-part-3",
    "428": "Zzts-city",
    "429": "Ls-yuki-1",
    "430": "Ls-yuki-2",
    "431": "Scarlet-green",
    "432": "Ls-akware-death",
    "433": "village",
    "434": "Ls-sas-1",
    "435": "Ls-sas-2",
    "436": "November-eve",
    "437": "Secret-agent-chronicles",
    "438": "Ls-ravenfall",
    "439": "Caves-of-zzt-walkthrough",
    "440": "City-of-zzt-walkthrough",
    "441": "Dungeons-of-zzt-walkthrough",
    "442": "Town-of-zzt-walkthrough",
    "443": "November-eve-b",
    "444": "Ls-shootwrong",
    "445": "Town-of-zzt-map",
    "446": "compound",
    "447": "Ls-blind-remix",
    "448": "Ls-sonic",
    "449": "winter",
    "450": "Ls-small-spaces",
    "451": "Police-quest-plus",
    "452": "Ls-cannibal-island",
    "453": "Joy-0",
    "454": "Joy-1",
    "455": "Joy-2",
    "456": "Joy-3",
    "457": "Joy-4",
    "458": "mistakes",
    "459": "decade",
    "460": "Joy-5",
    "461": "Nuclear-madman",
    "462": "Zombinator-walkthrough",
    "463": "Joy-6",
    "464": "Ls-balrog",
    "465": "Joy-7",
    "466": "Dragon-woods",
    "467": "Secret-agent-chronicles-2",
    "468": "deconstruction",
    "469": "Joy-8",
    "470": "baloo",
    "471": "Ls-variety",
    "472": "Ls-joe-moe-1",
    "473": "Ls-joe-moe-2",
    "474": "Ls-selectbutton-jam",
    "475": "Ls-predator",
    "476": "Ls-artificer",
    "477": "Joy-9",
    "478": "demos",
    "479": "Ls-cdslash",
    "480": "Invasion-zzt",
    "481": "Ls-quest-for-the-immortals",
    "482": "Ls-mystery-manor",
    "483": "Ls-burger-joint",
    "484": "Invasion-zzt",
    "485": "yiepipipi",
    "486": "Ls-time",
    "487": "ls-summer-2000-24hoz",
    "488": "ls-july-2020-bkzzt",
    "489": "zyla",
    "490": "publishing",
    "491": "Ls-fury-spell",
    "492": "Fg-chowder",
    "493": "Fg-cat-cat",
    "494": "We-are-still-out-here",
    "495": "Ls-kiyb",
    "496": "cdslash",
    "497": "Ls-dark-citadel-1",
    "498": "Ls-dark-citadel-2",
    "499": "Ls-second-earth",
    "500": "Z-files",
    "501": "Ls-oadm",
    "502": "For-elise",
    "503": "fmv",
    "504": "Ls-oktrollberfest-1",
    "505": "Ls-oktrollberfest-2",
    "506": "Ls-invasion-zzt-1",
    "507": "wuastw",
    "508": "Ls-oktrollberfest-results",
    "509": "Ls-invasion-zzt-2",
    "510": "Sids-disaster",
    "511": "Ls-advent",
    "512": "Growing-up",
    "513": "Ls-town",
    "514": "Ls-caves-of-fury",
    "515": "30th-documents-1",
    "516": "Ls-dungeons",
    "517": "Ls-zzts-city",
    "518": "Epic-mega-haul",
    "519": "Love-letters",
    "520": "Legend-of-brandonia",
    "521": "Ls-shades-of-gray",
    "522": "Ls-town-remix-1",
    "523": "Ls-town-remix-2",
    "524": "Lp-metal-saviour-bia",
    "525": "Lp-madam-grizelda",
    "526": "Lp-oreo-the-hamster",
    "527": "Ls-town-remix-3",
    "528": "Ls-cyber-purge",
    "529": "Speed-racer-x",
    "530": "Speed-racer-x",
    "531": "test",
    "532": "test",
}


def main():
    if len(sys.argv) < 2:
        print("Modernize single article: modernize-article.py <article_id>")
        print("Modernize all articles: export-article.py A")
        return False

    root_path = input("Input path (blank for current dir): ")

    if sys.argv[-1] == "A":
        files = glob.glob(os.path.join(root_path, "*.html"))
    else:
        files = glob.glob(os.path.join(root_path, sys.argv[1] + ".html"))

    for f in files:
        print(f)
        with open(f) as fh:
            a_id = int(f.split("/")[-1][:-5])
            a = Article.objects.get(pk=a_id)
            mode = "scan"
            content = []
            for line in fh.readlines():
                # Find content start
                if mode == "scan":
                    if line == "<!-- CONTENT BEGIN -->\n":
                        mode = "content"
                elif mode == "content":
                    content.append(line)
            print("Read", len(content), " lines of content")

            # Improve Links
            print("=" * 80)
            print("IMPROVING LINKS")
            content = improve_links(content)

            # Update static
            print("=" * 80)
            print("UPDATING STATIC REFERENCES")
            content = update_static(content)

            print("=" * 80)
            print("UPDATING ETC")
            content = update_etc(content, a)

            # Write new file
            with open("new-" + f, "w") as nfh:
                nfh.write("".join(content))
                print("Wrote", "new-" + f)

    # Update database
    if sys.argv[-1] == "A":
        files = glob.glob("new-articles/*.html")
        for f in files:
            a_id = int(f.split("/")[-1][:-5])
            with open(f) as fh:
                a = Article.objects.get(pk=a_id)
                a.content = fh.read()
                a.static_directory = STATIC_DIRS.get(str(a_id), "").lower()
                a.save()
                print(a.static_directory, "|", a.title)



def improve_links(content):
    output = []
    line_num = 1
    for line in content:
        changed = False
        if "href=" in line:
            if "http://museumofzzt.com/" in line:
                line = line.replace("http://museumofzzt.com/", "/")
                changed = True
            if "https://museumofzzt.com/" in line:
                line = line.replace("https://museumofzzt.com/", "/")
                changed = True

            if "target=" not in line:
                print("MISSING TARGET ON LINE #" + str(line_num))

        if changed:
            print(line)
        output.append(line)
        line_num += 1

    return output


def update_static(content):
    output = []
    line_num = 13  # Skip the header
    for line in content:
        changed = False
        if "zzt_img" in line:
            split = line.split(" ")
            #print(line)

            idx = 0
            for piece in split:
                print(split)
                if piece and (piece[0] == "'" or piece[0] == '"'):
                    split[idx] = "path '{}".format(split[idx].split("/")[-1])
                idx += 1
                changed = True

        if changed:
            line = " ".join(split)
            #print(line)
        output.append(line)
        line_num += 1

    return output


def update_etc(content, a):
    output = []
    line_num = 13  # Skip the header

    year = a.publish_date.year
    if year == 1970:
        year = "unk"

    for line in content:
        changed = False
        if "/static/images/featured/" in line:
            replacement = "/static/articles/{}/{}/".format(year, STATIC_DIRS.get(str(a.id), "").lower())
            line = line.replace("/static/images/featured/", replacement)
        elif "static '/images/articles/cl/2020/for-elise/" in line:
            replacement = "static 'articles/2020/for-elise/"
            line = line.replace("static '/images/articles/cl/2020/for-elise/", replacement)
        elif "/static/images/articles/cl/2020/wuastw/" in line:
            replacement = "/static/articles/2020/wuastw/"
            line = line.replace("/static/images/articles/cl/2020/wuastw/", replacement)
        elif "images/articles/cl/2020/fmv" in line:
            replacement = "articles/2020/fmv"
            line = line.replace("images/articles/cl/2020/fmv", replacement)

        elif "/static/images/articles/cl/2020/cdslash/" in line:
            replacement = "/static/articles/2020/cdslash/"
            line = line.replace("/static/images/articles/cl/2020/cdslash/", replacement)
        elif "/static/images/articles/newsletter" in line:
            replacement = "/static/articles/{}/{}/".format(year, STATIC_DIRS.get(str(a.id), "").lower())
            line = line.replace("/static/images/articles/newsletter/", replacement)
        elif "images/articles/cl/2020/publishing/" in line:
            replacement = "articles/2020/publishing/"
            line = line.replace("images/articles/cl/2020/publishing/", replacement)
        elif "{% static 'images/articles/cl/2020/winter/" in line:
            replacement = "{% " + "static 'articles/2020/winter/"
            line = line.replace("{% static 'images/articles/cl/2020/winter/", replacement)
        elif "{% static 'images/articles/cl/2020/dragon-woods/" in line:
            replacement = "{% " + "static 'articles/2020/dragon-woods/"
            line = line.replace("{% static 'images/articles/cl/2020/dragon-woods/", replacement)
        elif "<video src=\"{% static 'images/articles/cl/" in line:
            replacement = "<video src=\"{% " + "static 'articles/"
            line = line.replace("<video src=\"{% static 'images/articles/cl/", replacement)
        elif "<video src=\"{% static '/images/articles/cl/" in line:
            replacement = "<video src=\"{% " + "static 'articles/"
            line = line.replace("<video src=\"{% static '/images/articles/cl/", replacement)
        elif "<audio src=\"{% static 'images/articles/cl/" in line:
            replacement = "<audio src=\"{% " + "static 'articles/"
            line = line.replace("<audio src=\"{% static 'images/articles/cl/", replacement)
        elif "/static/images/articles/bugs/player-clones/" in line:
            replacement = "/static/articles/2018/bugs-player-clones/"
            line = line.replace("/static/images/articles/bugs/player-clones/", replacement)
        elif "images/featured/16/" in line:
            replacement = "articles/2018/fg-sixteen-easy-pieces/"
            line = line.replace("images/featured/16/", replacement)
        elif "{% static 'images/articles/frost-ost/" in line:
            replacement = "{% static 'articles/2019/frost-ost/"
            line = line.replace("{% static 'images/articles/frost-ost/", replacement)
        elif "/static/images/articles/frost-ost/" in line:
            replacement = "/static/articles/2019/frost-ost/"
            line = line.replace("/static/images/articles/frost-ost/", replacement)
        elif "images/articles/zeta/" in line:
            replacement = "articles/2019/zeta/"
            line = line.replace("images/articles/zeta/", replacement)
        elif "static 'images/articles/cl/2020/decade/" in line:
            replacement = "static 'articles/2020/decade/"
            line = line.replace("static 'images/articles/cl/2020/decade/", replacement)
        elif "images/articles/walkthrough/zombinator/THE ZOMBINATOR Spoilers.pdf":
            replacement = "/articles/2020/zombinator-walkthrough/THE ZOMBINATOR Spoilers.pdf"
            line = line.replace("images/articles/walkthrough/zombinator/THE ZOMBINATOR Spoilers.pdf", replacement)


        elif "'images/articles/zzt-versions/dl-button-zzt-32.png'" in line:
            line = line.replace("'images/articles/zzt-versions/dl-button-zzt-32.png'", "'articles/2015/zzt-versions/dl-button-zzt-32.png'")
        elif "{% static 'images/articles/cl/" in line:
            replacement = "{% static 'articles/" + "{}/".format(year)
            line = line.replace("{% static 'images/articles/cl/", replacement)
        elif "/static/images/articles/cl/" in line:
            replacement = "/static/articles/" + "{}/".format(year)
            line = line.replace("/static/images/articles/cl/", replacement)
        elif "{% static 'images/articles/walkthrough/sixteen-easy-pieces/" in line:
            replacement = "{% " + "static 'articles/{}/{}/".format(year, STATIC_DIRS.get(str(a.id), "").lower())
            line = line.replace("{% static 'images/articles/walkthrough/sixteen-easy-pieces/", replacement)

        output.append(line)
        line_num += 1

    return output

if __name__ == '__main__':
    main()

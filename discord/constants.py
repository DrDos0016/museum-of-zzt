from django.conf import settings

if settings.ENVIRONMENT == "DEV":
    WOZZT_URL = "http://django.pi:8000/api/worlds-of-zzt/?category=discord"
else:
    WOZZT_URL = "https://museumofzzt.com/api/worlds-of-zzt/?category=discord"

COOLDOWN_MESSAGE = "`!{}` is on cooldown for {} more second(s)."

HELP = """```
List of commands:
  !addrole [role]       Add one or more roles.
  !help                 Shows this message.
  !link [category]      Show a list of links for a category
  !removerole [role]    Remove a role.
  !scroll [#]           Some reading material. (10 sec. cooldown)
  !zzt                  Shows a random ZZT board. (15 sec. cooldown)

List of roles:
  ZZTer       MZXer
  He/Him      She/Her     They/Them
  Stream-Alerts-All       Stream-Alerts-Asie
  Stream-Alerts-Dos       Stream-Alerts-Meap

List of categories:
  Programs    Editors
  Resources   Worlds

Some commands are restricted to specific channels. All commands function in the #bots channel.
```"""

# Framing for !scroll
SCROLL_TOP = """```
╞╤═════════════════════════════════════════════╤╡
 │                  Scroll ##                  │
 ╞═════════════════════════════════════════════╡
 │    •    •    •    •    •    •    •    •    •│"""

SCROLL_BOTTOM = """\n │    •    •    •    •    •    •    •    •    •│
╞╧═════════════════════════════════════════════╧╡```"""

# Text for !links
PROGRAMS_TEXT = """**Programs**
:slight_smile: [ZZT v3.2](<https://museumofzzt.com/file/view/zzt/>) - The final official registered ZZT release with the original worlds included. Requires Zeta to run on modern systems.
:construction_worker: [The Reconstruction of ZZT](<https://github.com/asiekierka/reconstruction-of-zzt/releases/tag/v1.0>) - Identical to ZZT v3.2 sans the inclusion of registered worlds. Useful for modern standalone ZZT releases as it won't be blabbing about not distributing the program.
:floppy_disk: [Zeta](<http://zeta.asie.pl/>) - Emulator necessary to run DOS based ZZT and Super ZZT executables on modern systems. Supports audio and gif recording plus a dedicated web version to allow ZZT worlds to be played in a browser.
:lion_face: [ClassicZoo](<https://zeta.asie.pl/wiki/doku.php?id=release:classiczoo>) - Enhanced fork of ZZT with numerous convenience features for players, an improved editor, and increased limits while maintaining compatibility with worlds designed for ZZT v3.2. Has native Windows and Linux builds in addition to an MS-DOS build compatible with Zeta
:thread: [Weave ZZT](<https://meangirls.itch.io/weave-3>) - Enhanced fork of ZZT designed to maintain the spirit of the original while eliminating the need to exploit glitches, and write tedious code in order to deal with ZZT's limitations."""

EDITORS_TEXT = """**Editors:**
:regional_indicator_k: [KevEdit](<https://github.com/cknave/kevedit/releases>) - External editor with an interface based on ZZT's own. Releases for DOS, Windows, and Linux are readily available. Popular both with returning ZZTers who have used it in the past as well as those only familiar with ZZT's original editor.
:regional_indicator_z: [zedit2](<https://zedit2.skyend.net/>) - New editor with a more mouse-driven interface, support for Super ZZT worlds, image conversion, atlas making, and expert level features while still being an excellent option for newcomers.
:thread: [LOOMZZT/ZLOOM2](<https://meangirls.itch.io/weave-3>) - Forks of KevEdit and zedit2 designed around the limitations of Weave rather than ZZT v3.2
**Tools**
:frame_photo: [zima](<https://github.com/asiekierka/zima/releases>) - Convert images to ZZT, Super ZZT, Weave ZZT, and MegaZeux boards with a lot of customization options. ZZT-OOP code linting to detect issues and bugs with 3.2 worlds.
:musical_keyboard: [SFX Tracker](<https://www.digitalmzx.com/show.php?id=2589>) - A PC speaker tracker program built for MegaZeux designed to output ZZT-OOP #play commands."""

RESOURCES_TEXT = """**Wikis**
:sewing_needle: [Wiki of Weavers](<https://zeta.asie.pl/wiki/doku.php?id=start>) Information on file formats, forks, clones, and ZZT preservation information
:slight_smile: [Wiki of ZZT](<https://wiki.zzt.org/wiki/Main_Page>) - Information on ZZT's elements, ZZT-OOP, ZZT's sounds, and jargon
**Helpful Museum Articles**
:art: [*The Joy of ZZT*](<https://museumofzzt.com/series/8/the-joy-of-zzt/?sort=date>) (2020) -  YouTube series depicting the full creation of a ZZT world designed for newcomers. A gentle introduction to ZZT-OOP all the way through creating a unique engine
:tools: [*Modern Tools and Resources*](<https://museumofzzt.com/article/view/651/modern-tools-and-resources/>) (2021) - A slightly more in-depth look at some of the tools used for creating ZZT worlds.
:blue_book: [*The Unofficial ZZT Player's Manual*](<https://museumofzzt.com/article/view/737/the-unofficial-zzt-players-manual/>) (2022) - Guide to getting started playing ZZT, downloading engines, basic gameplay elements, cheats, and a complete overview of all the elements that make up ZZT worlds.
:computer: [*ZZT-OOP 101*](<https://museumofzzt.com/article/view/747/zzt-oop-101/>) (2022) - A beginner oriented guide to ZZT-OOP programming
:pencil: [*Learning ZZT-OOP By Example*](<https://museumofzzt.com/article/view/756/learning-zzt-oop-by-example-with-examplia/>) (2022) - Practical demonstrations of every ZZT-OOP command with an accompanying example world. Going through all the code and explaining the hows and whys of ZZT-OOP programming.
:floppy_disk: [*ZZT to the Masses*](<https://museumofzzt.com/article/view/490/zzt-to-the-masses-publishing-to-the-museum-and-itchio/>) (2020) - Guide for publishing ZZT worlds onto Itch.io and the Museum of ZZT. Plus how to set up a web version of Zeta in order to allow your game to be played directly in a web browser.
:sos: [*Help Directory*](<https://museumofzzt.com/article/category/help/>) - Any article on the Museum of ZZT categorized as "help"."""

WORLDS_TEXT = """**World Recommendations**
:trophy: [*The Best of ZZT*](<https://museumofzzt.com/article/view/295/the-best-of-zzt/>) (2018) - Recommendations focused on traditional ZZT gameplay, well-polished titles, unexpected gameplay styles, artistic endeavors, and a few generic suggestions for types of worlds to keep an eye opened for.
:trophy: [*The Best of ZZT Part 2 - Modern Treasures*](<https://museumofzzt.com/article/view/563/the-best-of-zzt-part-2-modern-treasures/>) (2021) - Recommendations focused on worlds created by the present day ZZT community, as well as a few fun older titles that were overlooked in the previous article.
:beginner: [*Beginner Friendly Worlds*](<https://museumofzzt.com/collection/view/beginner-friendly-worlds/>) - A collection of worlds for newcomers meant to provide an idea of what ZZT games can be that require little to no prior knowledge of ZZT's mechanics"""

INVALID_LINK_TEXT = "Please specify a category of 'Programs', 'Resources', 'Editors', or 'Worlds'. (ex: !link worlds)"

LINKS = {"programs": PROGRAMS_TEXT, "editors": EDITORS_TEXT, "resources": RESOURCES_TEXT, "worlds": WORLDS_TEXT}

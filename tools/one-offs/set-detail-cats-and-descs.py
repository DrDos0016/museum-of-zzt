import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402

DESCRIPTIONS = {
1: "Uploaded files which are designed to be used in an MS-DOS compatible environment. This detail is partially defunct and may be removed in the future.",
7: "Uploaded files which have been recognized in some way for their quality or other notable attributes. These files mostly consist of those which won historical \"Game of the Month\", \"Classic Game of the Month\", \"Featured Game\", and \"M‍a‍d‍T‍o‍m‍'‍s Pick\" awards. They may randomly appear in the spotlight on most Museum pages. Do note that changing tastes over time mean that not all Featured Worlds are necessarily great games to play today. If you're looking for recommendations see <a href=\"/article/295/the-best-of-zzt\" target=\"_blank\">The Best of ZZT</a> and <a href=\"/article/563/the-best-of-zzt-part-2-modern-treasures\" target=\"_blank\">The Best of ZZT Part 2 - Modern Treasures</a>.",
9: "Uploaded files which contain one or more ZZM Audio files in <span class=\"cp437\">.ZZM</span> format. This is a legacy format created in the late 1990s to allowing listening to ZZT game soundtracks in dedicated ZZM players. These players are inaccurate to ZZT's actual audio systems. The players frequently crash in DOSBox as well making the format poorly supported on modern devices. These are <b>partially</b> supported by the Museum's file viewer in that they can be viewed as text, but cannot be played. New creations should avoid using the ZZM format for a soundtrack release and opt to record from Zeta instead.",
10: "Uploaded files which contain one or more alternate character sets or palettes for (Super) ZZT worlds. These files are typically designed for an included (Super) ZZT world, though some may be generic modifications intended to be used with any world. Most of these files include a <span class=\"cp437\">.BAT</span> file to load the custom graphics, launch ZZT, and then unload the graphics. To properly run these with Zeta, consult the program's documentation and <a href=\"/zeta\" target=\"_blank\">Using ZZT with Zeta</a>. These files are <b>partially</b> supported by the Museum's file viewer. Custom fonts must be manually converted to PNG files for the file viewer and will automatically load when available for a file. Custom palettes are currently not supported.",
11:"Uploaded files which contain one or more modified versions of (Super) ZZT. In the past these were made by hex editing the official ZZT v3.2 release to mute sounds, suppress messages, and increase memory allocation. Today modifications to ZZT are done at the source level by making changes to <a href=\"https://github.com/asiekierka/reconstruction-of-zzt\" target=\"_blank\">The Reconstruction of ZZT</a> and <a href=\"https://github.com/asiekierka/reconstruction-of-super-zzt\" target=\"_blank\">Super</a> code-bases. At this time, newly created custom modifications to ZZT made are recommended to be bundled with worlds designed for them.",
13:"Uploaded files which contain one or more Super ZZT world (<span class=\"cp437\">.SZT</span>) files. These files are modules for Super ZZT and/or various forks and source ports. The vast majority are designed to run with Super ZZT v2.0. Worlds requiring alternative methods of play usually state how to run them in included documentation. These are supported by the Museum's file viewer.",
14:"Uploaded files which contain programs specifically to aid in the creation of ZZT and related files or sometimes just miscellaneous items as a legacy thing from the z2 days. Keep in mind that many utilities are quite old and are designed to be ran on systems that support MS-DOS programs. For utilities that are ZZT files rather than programs, check out the genre tags <a href=\"https://museumofzzt.com/search/?genre=Help\" target=\"_blank\">Help</a>, <a href=\"https://museumofzzt.com/search/?genre=Toolkit\" target=\"_blank\">Toolkit</a>, and <a href=\"https://museumofzzt.com/search/?genre=Utility\" target=\"_blank\">Utility</a>. Yes I realize how stupid that last sentence is.",
15:"Uploaded files which contain one or more ZZT world (<span class=\"cp437\">.ZZT</span>) files. These files are modules for ZZT and/or various forks and source ports. The vast majority are designed to run with ZZT v3.2. Worlds requiring alternative methods of play usually state how to run them in included documentation. These are supported by the Museum's file viewer.",
16:"Uploaded files which contain one or more worlds for the ZZT clone ZIG (<span class=\"cp437\">.ZIG</span>) files. These files are modules for ZIG (ZZT Inspired Game Creation System), a ZZT clone whose worlds were officially accepted into <a href=\"http://zzt.org\" target=\"_blank\">z2</a>'s archives. Due to its status and the fact that unlike most ZZT clones it has a few actual games made by authors other than ZIG's developer, these files are specifically marked as such rather than using the more generic \"Clone World\" detail. These are <b>NOT</b> supported by the Museum of ZZT's file viewer.",
17:"Uploaded files that aren't uploaded. These files are known to have existed at one point but no known copies are available. If you have them, please upload! This list is also very much incomplete and is mostly based on data coming from z2's database. If you're trying to track down lost ZZT worlds consider the <a href=\"https://zeta.asie.pl/wiki/doku.php?id=research:lost_zzt_files\">Lost ZZT Files</a> page on the Wiki of Weavers.",
18:"Uploaded files which have not yet been properly looked at by staff. These files are marked as such as a way of saying that they should be downloaded and ran at your own risk. Uploaded files can't be reviewed. They are <b>partially</b> supported by the Museum's file viewer and Play Online features where they assume default settings prior to publication and may not function as intended until properly configured. Uploaded files may be replaced at any time by the uploader prior to publication.",
19:"Removed Files. This detail and description should not be visible anywhere on the Museum.",
20:"Uploaded files which contain one or more corrupt (Super) ZZT (clone) worlds. These files have been damaged in some way which may render them unplayable or unfinishable. These are <b>partially</b> supported by the Museum's file viewer which will do its best to access non-corrupt boards. If you have an uncorrupt version of a corrupt world, please upload it! Please note that while the once-popular \"Super Lock\" will purposely corrupt the final board of a ZZT world (which in some cases renders a game unfinishable if the author forgot to add an extra board to safely be corrupted) that this detail does not apply. This detail is intended to function as both a warning to those wishing to play such files as well as an open call to find non-corrupt versions or create restorations based on available data.",
21:"Uploaded files which contain one or more ZZT board (<span class=\"cp437\">.BRD</span>) files. These files are exported ZZT boards that can be easily imported into a ZZT world with \"T\" in most editors. These are supported by the Museum's file viewer.",
22:"Uploaded files which contain one or more ZZT save (<span class=\"cp437\">.SAV</span>) files. These files contain a saved state of the world during play. They are functionally identical to ZZT worlds with the exceptions of changing a single byte to mark the file as a save and the use of a different extension. These are supported by the Museum's file viewer.",
23:"Uploaded files which contain one or more Super ZZT board (<span class=\"cp437\">.BRD</span>) files. These files are exported Super ZZT boards that can be imported into a Super ZZT world with \"T\" in most editors. These are supported by the Museum's file viewer.",
24:"Uploaded files which contain one or more Super ZZT save (<span class=\"cp437\">.SAV</span>) files. These files contain a saved state of the world during play. They are functionally identical to Super ZZT worlds other than a single byte to mark the file as a save and the different extension. These are supported by the Museum's file viewer.",
25:"Uploaded files which contain one or more ZZT high score (<span class=\"cp437\">.HI</span>) files. These files contain up to thirty entries consisting of a final score and entered string of text. These are supported by the Museum's file viewer.",
26:"Uploaded files which contain one or more Super ZZT high score (<span class=\"cp437\">.HGS</span>) files. These files contain up to thirty entries consisting of a final score and entered string of text. These are supported by the Museum's file viewer.",
27:"Uploaded files which contain one or more worlds for non-MegaZeux, non-ZIG, and non-Weave ZZT clones. These are <b>NOT</b> supported by the Museum's file viewer. As most ZZT clones received few released worlds, the Museum of ZZT hosts them as there's no better place for them online. Worlds for ZIG should use the \"ZIG World\" detail listed below. Worlds for MegaZeux should be uploaded to <a href=\"https://www.digitalmzx.com/\" target=\"_blank\">DigitalMZX</a>.",
28:"Uploaded files which contain source code for programs or scripts intended to be executed as-is. All (Super) ZZT worlds and most clone worlds include this by definition and are not tagged as such. These files include code that can be compiled or executed on various platforms. These are partially supported by the Museum of ZZT's file viewer. Source code will be displayed like any other text file, however no syntax highlighting or other functionality is supported.",
29:"Uploaded files which contain one or more text files in formats ranging from TXT to DOC. These files may include documentation, text assets, and order forms. These are <b>partially</b> supported by the Museum's file viewer. All formats are treated as plain text which will cause display issues for more robust formats like <span class=\"cp437\">.DOC</span> files, though their content is usually still parse-able. New creations should only include text files that are used in conjunction with other files contained in the upload. For new creations avoid generic names like <span class=\"cp437\">readme.txt</span> as ZZT worlds usually share a directory with many others. Though not required, including some text file with information about your creation is strongly encouraged.",
30:"Uploaded files which contain one or more HTML documents. These files are typically manuals and documentation  for various ZZT worlds/utilities. These are <b>NOT</b> supported by the Museum's file viewer. New creations should <b>avoid</b> solely using HTML formatting for documentation.",
31:"Uploaded files which contain one or more image files in formats ranging from ICO to PNG. These files may include program icons, screenshots, maps, and logos. These are supported by the Museum's file viewer. New creations should only include image files that are used in conjuction with other files contained in the upload. Including screenshots of a game compatible with the Museum file viewer is discouraged but accepted.",
32:"Uploaded files which contain one or more video files in formats ranging from AVI to MP4. These are <b>NOT</b> supported by the Museum's file viewer. New creations should <b>NOT</b> include video files unless absolutely necessary. Upload size restrictions will likely make bundling videos with an upload impossible.",
33:"Uploaded files which contain one of more executables. These files are typically utilities to aid in working with ZZT in some way or game specific executables designed to be used with just the included upload. These files are <b>NOT</b> supported by the Museum's file viewer for obvious reasons.",
34:"Uploaded files which contain one or more compressed files in formats ranging from ZIP to RAR. These contents of these files are effectively hidden from the file viewer and play online site functionalities. These are <b>NOT</b> supported by the Museum's file viewer. New creations should generally avoid \"zips within zips\" in order to better facilitate access to preserved data.",
35:"Uploaded files which contain files intended for (console/handheld) emulators or patches intended to be applied to a ROM file. These files are typically ZZT worlds converted to run on other devices or patches to be applied to commercial ROMs to ZZTify them in some way. The Museum of ZZT will not host any copyright infringing roms and requires patches to be distributed instead. <s>Delete after 24 hours.</s>",
36: "Uploaded files which contain one or more audio files in formats ranging from MIDI to XM. These files are typically soundtracks, assets for various ZZT clones/utilities, or sometimes just weird files that were included in an upload. These are <b>NOT</b> supported by the Museum's file viewer. New creations should only include audio files that are used in conjunction with other files contained in the upload.",
37: "Uploaded files which contain content designed to be ran using Weave ZZT and not ZZT v3.2. <a href=\"https://meangirls.itch.io/weave-2\" target=\"_blank\">Weave ZZT</a> is an actively developed (as of 2022) ZZT fork that intends to enhance ZZT's abilities while maintaining its simplicity. These files often contain a copy of a version of Weave ZZT for the world(s) contained within. They are <b>partially</b> supported by the Museum's file viewer which assumes all ZZT files to follow the ZZT 3.2 format resulting in some data not being displayed, and many graphical changes to not be properly handled.",
}

CATEGORIES = {
1: "Other",
7: "Other",
9: "Media",
10: "Other",
11: "Other",
13: "SZZT",
14: "Other",
15: "ZZT",
16: "Other",
17: "Other",
18: "Other",
19: "Other",
20: "Other",
21: "ZZT",
22: "ZZT",
23: "SZZT",
24: "SZZT",
25: "ZZT",
26: "SZZT",
27: "Other",
28: "Other",
29: "Media",
30: "Media",
31: "Media",
32: "Media",
33: "Other",
34: "Other",
35: "Other",
36: "Media",
37: "Other"
}

def main():
    qs = Detail.objects.all().order_by("pk")
    for d in qs:
        print(d.id, d.detail)
        if DESCRIPTIONS.get(d.id):
            d.description = DESCRIPTIONS[d.id]
        if CATEGORIES.get(d.id):
            d.category = CATEGORIES[d.id]
        d.save()
    return True


if __name__ == '__main__':
    main()

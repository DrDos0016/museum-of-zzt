import os

from museum_site.core.detail_identifiers import *
from museum_site.models.detail import Detail

class File_Extension_Info(object):
    def __init__(self, extension, name="", associated_details=[], file_viewer_type="", file_viewer_func="", ambiguous=False):
        self.extension = extension
        self.name = name
        self.associated_details = associated_details
        self.file_viewer_type = file_viewer_type
        self.file_viewer_func = file_viewer_func
        self.ambiguous = ambiguous


EXTENSIONS = {
    # ZZT
    ".BRD": File_Extension_Info(".BRD", "Board File", [DETAIL_ZZT_BOARD], ambiguous=True),
    ".ZZT": File_Extension_Info(".ZZT", "ZZT World", [DETAIL_ZZT]),
    ".Z_T": File_Extension_Info(".ZZT", "ZZT World", [DETAIL_ZZT]),
    ".HI": File_Extension_Info(".HI", "High Score File", [DETAIL_ZZT_SCORE], ambiguous=True),
    ".MH": File_Extension_Info(".MH", "Mystical Winds ZZT High Score File", [DETAIL_ZZT_SCORE]),
    ".MWZ": File_Extension_Info(".MWZ", "Mystical Winds ZZT World", [DETAIL_ZZT]),
    ".SAV": File_Extension_Info(".MWZ", "Mystical Winds ZZT World", [DETAIL_ZZT_SAVE], ambiguous=True),

    # Super ZZT
    ".SZT": File_Extension_Info(".SZT", "Super ZZT World", [DETAIL_SZZT]),
    ".HGS": File_Extension_Info(".HGS", "Super ZZT High Score File", [DETAIL_SZZT_SCORE]),

    # Charsets
    ".CHR": File_Extension_Info(".CHR", "Charset", [DETAIL_GFX]),
    ".COM": File_Extension_Info(".COM", "Charset", [DETAIL_GFX], ambiguous=True),
    ".FNT": File_Extension_Info(".COM", "Charset", [DETAIL_GFX]),

    # Palettes
    ".PAL": File_Extension_Info(".PAL", "Palette", [DETAIL_GFX]),
    ".PLD": File_Extension_Info(".PLD", "Palette", [DETAIL_GFX]),

    # ZIG
    ".INF": File_Extension_Info(".INF", "ZIG Information File", ambiguous=True),
    ".ZIG": File_Extension_Info(".ZIG", "ZIG World", [DETAIL_ZIG]),
    ".ZBR": File_Extension_Info(".ZBR", "ZIG Board"),
    ".ZCH": File_Extension_Info(".ZCH", "ZIG Charset"),
    ".ZPL": File_Extension_Info(".ZPL", "ZIG Palette"),
    ".OLF": File_Extension_Info(".OLF", "ZIG Object Library File"),

    # ZZM
    ".ZZM": File_Extension_Info(".ZZM", "ZZM Audio"),

    # ZZT Clone Worlds
    ".ZZ3": File_Extension_Info(".ZZ3", "ZZ3 World", [DETAIL_CLONE_WORLD]),
    ".SWW": File_Extension_Info(".SWW", "SuperWAD World", [DETAIL_CLONE_WORLD]),
    ".PGF": File_Extension_Info(".PGF", "Platic Game File", [DETAIL_CLONE_WORLD]),
    ".PWORLD": File_Extension_Info(".PWORLD", "Plastic Game File", [DETAIL_CLONE_WORLD]),

    # Source Code
    ".ASM": File_Extension_Info(".ASM", "Assembly Source Code", [DETAIL_SOURCE_CODE]),
    ".BAS": File_Extension_Info(".BAS", "BASIC Source Code", [DETAIL_SOURCE_CODE]),
    ".BI": File_Extension_Info(".BI", "Source Code", [DETAIL_SOURCE_CODE]),
    ".C": File_Extension_Info(".C", "C Source Code", [DETAIL_SOURCE_CODE]),
    ".CC": File_Extension_Info(".CC", "Source Code", [DETAIL_SOURCE_CODE]),
    ".CPP": File_Extension_Info(".CPP", "C++ Source Code", [DETAIL_SOURCE_CODE]),
    ".E": File_Extension_Info(".E", "Euphoria Source Code", [DETAIL_SOURCE_CODE]),
    ".EX": File_Extension_Info(".EX", "Source Code", [DETAIL_SOURCE_CODE]),
    ".H": File_Extension_Info(".H", "Source Code", [DETAIL_SOURCE_CODE]),
    ".JAVA": File_Extension_Info(".JAVA", "Java Source Code", [DETAIL_SOURCE_CODE]),
    ".INC": File_Extension_Info(".INC", "Source Code", [DETAIL_SOURCE_CODE]),
    ".LUA": File_Extension_Info(".LUA", "Lua Source Code", [DETAIL_SOURCE_CODE]),
    ".PAS": File_Extension_Info(".PAS", "Pascal Source Code", [DETAIL_SOURCE_CODE]),
    ".PY": File_Extension_Info(".PY", "Python Source Code", [DETAIL_SOURCE_CODE]),

    # Plaintext
    ".135": File_Extension_Info(".135", "Text File", [DETAIL_TEXT]),
    ".ASC": File_Extension_Info(".ASC", "Text File", [DETAIL_TEXT]),
    ".1ST": File_Extension_Info(".1ST", "Text File", [DETAIL_TEXT]),
    ".ANS": File_Extension_Info(".ANS", "Text File", [DETAIL_TEXT]),
    ".BAT": File_Extension_Info(".BAT", "Text File", [DETAIL_TEXT]),
    ".BB": File_Extension_Info(".BB", "Text File", [DETAIL_TEXT]),
    ".CFG": File_Extension_Info(".CFG", "Text File", [DETAIL_TEXT]),
    "COPYING": File_Extension_Info("COPYING", "Text File", [DETAIL_TEXT]),
    ".CRD": File_Extension_Info(".CRD", "Text File", [DETAIL_TEXT]),
    ".DAT": File_Extension_Info(".DAT", "Text File", [DETAIL_TEXT], ambiguous=True),
    "DESC": File_Extension_Info("DESC", "Text File", [DETAIL_TEXT]),
    ".DEF": File_Extension_Info(".DEF", "Text File", [DETAIL_TEXT]),
    ".DEU": File_Extension_Info(".DEU", "Text File", [DETAIL_TEXT]),
    ".DIZ": File_Extension_Info(".DIZ", "Text File", [DETAIL_TEXT]),
    ".DOC": File_Extension_Info(".DOC", "Text File", [DETAIL_TEXT]),
    ".EED": File_Extension_Info(".EED", "Text File", [DETAIL_TEXT]),
    ".ENG": File_Extension_Info(".ENG", "Text File", [DETAIL_TEXT]),
    ".ERR": File_Extension_Info(".ERR", "Text File", [DETAIL_TEXT]),
    "EXCLUDE": File_Extension_Info("EXCLUDE", "Text File", [DETAIL_TEXT]),
    ".FAQ": File_Extension_Info(".FAQ", "Text File", [DETAIL_TEXT]),
    ".FLG": File_Extension_Info(".FLG", "Text File", [DETAIL_TEXT]),
    ".FRM": File_Extension_Info(".FRM", "Text File", [DETAIL_TEXT]),
    ".FYI": File_Extension_Info(".FYI", "Text File", [DETAIL_TEXT]),
    ".GITIGNORE": File_Extension_Info(".GITIGNORE", "Text File", [DETAIL_TEXT]),
    ".GUD": File_Extension_Info(".GUD", "Text File", [DETAIL_TEXT]),
    ".HINTS": File_Extension_Info(".HINTS", "Text File", [DETAIL_TEXT]),
    ".HLP": File_Extension_Info(".HLP", "Text File", [DETAIL_TEXT]),
    ".INI": File_Extension_Info(".INI", "Text File", [DETAIL_TEXT]),
    ".JSON": File_Extension_Info(".JSON", "Text File", [DETAIL_TEXT]),
    ".KB": File_Extension_Info(".KB", "Text File", [DETAIL_TEXT]),
    "LASTSG": File_Extension_Info(".LASTSG", "Text File", [DETAIL_TEXT]),
    "LICENSE": File_Extension_Info("LICENSE", "Text File", [DETAIL_TEXT]),
    "LPT1": File_Extension_Info("LPT1", "Text File", [DETAIL_TEXT]),
    ".LOG": File_Extension_Info(".LOG", "Text File", [DETAIL_TEXT]),
    ".LST": File_Extension_Info(".LST", "Text File", [DETAIL_TEXT]),
    ".MAC": File_Extension_Info(".MAC", "Text File", [DETAIL_TEXT]),
    ".MAP": File_Extension_Info(".MAP", "Text File", [DETAIL_TEXT]),
    ".MD": File_Extension_Info(".MD", "Text File", [DETAIL_TEXT]),
    ".ME": File_Extension_Info(".ME", "Text File", [DETAIL_TEXT]),
    ".MSG": File_Extension_Info(".MSG", "Text File", [DETAIL_TEXT]),
    ".MUZ": File_Extension_Info(".MUZ", "Text File", [DETAIL_TEXT]),
    ".NEW": File_Extension_Info(".NEW", "Text File", [DETAIL_TEXT]),
    "NEWS": File_Extension_Info("NEWS", "Text File", [DETAIL_TEXT]),
    ".NFO": File_Extension_Info(".NFO", "Text File", [DETAIL_TEXT]),
    ".NOW": File_Extension_Info(".NOW", "Text File", [DETAIL_TEXT]),
    ".OBJ": File_Extension_Info(".OBJ", "Text File", [DETAIL_TEXT]),
    "ORDER": File_Extension_Info("ORDER", "Text File", [DETAIL_TEXT]),
    ".OOP": File_Extension_Info(".OOP", "Text File", [DETAIL_TEXT]),
    ".PAR": File_Extension_Info(".PAR", "Text File", [DETAIL_TEXT]),
    ".PDF": File_Extension_Info(".PDF", "Text File", [DETAIL_TEXT]),
    "README": File_Extension_Info("README", "Text File", [DETAIL_TEXT]),
    ".REG": File_Extension_Info(".REG", "Text File", [DETAIL_TEXT]),
    "REGISTER": File_Extension_Info(".REGISTER", "Text File", [DETAIL_TEXT]),
    ".RTF": File_Extension_Info(".RTF", "Text File", [DETAIL_TEXT]),
    "SAVES": File_Extension_Info("SAVES", "Text File", [DETAIL_TEXT]),
    ".SDI": File_Extension_Info(".SDI", "Text File", [DETAIL_TEXT]),
    ".SH": File_Extension_Info(".SH", "Text File", [DETAIL_TEXT]),
    ".SOL": File_Extension_Info(".SOL", "Text File", [DETAIL_TEXT]),
    ".SLV": File_Extension_Info(".SLV", "Text File", [DETAIL_TEXT]),
    ".ST": File_Extension_Info(".ST", "Text File", [DETAIL_TEXT]),
    ".THEME": File_Extension_Info(".THEME", "Text File", [DETAIL_TEXT]),
    ".TXT": File_Extension_Info(".TXT", "Text File", [DETAIL_TEXT]),
    "WORLDS": File_Extension_Info("WORLDS", "Text File", [DETAIL_TEXT]),
    ".WPS": File_Extension_Info(".WPS", "Text File", [DETAIL_TEXT]),
    ".WRI": File_Extension_Info(".WRI", "Text File", [DETAIL_TEXT]),
    ".ZLN": File_Extension_Info(".ZLN", "Text File", [DETAIL_TEXT]),
    ".ZML": File_Extension_Info(".ZML", "Text File", [DETAIL_TEXT]),
    ".ZZL": File_Extension_Info(".ZZL", "Text File", [DETAIL_TEXT]),

    # HTML
    ".HTM": File_Extension_Info(".HTM", "HTML File", [DETAIL_HTML]),
    ".HTML": File_Extension_Info(".HTML", "HTML File", [DETAIL_HTML]),

    # Audio
    ".IT": File_Extension_Info(".IT", "Audio File", [DETAIL_AUDIO]),
    ".MID": File_Extension_Info(".MID", "Audio File", [DETAIL_AUDIO]),
    ".MIDI": File_Extension_Info(".MIDI", "Audio File", [DETAIL_AUDIO]),
    ".MOD": File_Extension_Info(".MOD", "Audio File", [DETAIL_AUDIO]),
    ".MP3": File_Extension_Info(".MP3", "Audio File", [DETAIL_AUDIO]),
    ".WAV": File_Extension_Info(".WAV", "Audio File", [DETAIL_AUDIO]),
    ".XM": File_Extension_Info(".XM", "Audio File", [DETAIL_AUDIO]),
    ".PTF":File_Extension_Info(".PTF", "Audio File", [DETAIL_AUDIO]),

    # Image
    ".BMP": File_Extension_Info(".BMP", "Image File", [DETAIL_IMAGE]),
    ".GIF": File_Extension_Info(".GIF", "Image File", [DETAIL_IMAGE]),
    ".ICO": File_Extension_Info(".ICO", "Image File", [DETAIL_IMAGE]),
    ".JPG": File_Extension_Info(".JPG", "Image File", [DETAIL_IMAGE]),
    ".JPEG": File_Extension_Info(".JPEG", "Image File", [DETAIL_IMAGE]),
    ".PCX": File_Extension_Info(".PCX", "Image File", [DETAIL_IMAGE]),
    ".PNG": File_Extension_Info(".PNG", "Image File", [DETAIL_IMAGE]),

    # Video
    ".ACI": File_Extension_Info(".AVI", "Video File", [DETAIL_VIDEO]),

    # Programs
    # .COM is assumed font over program
    ".EXE": File_Extension_Info(".EXE", "Executable", [DETAIL_PROGRAM]),
    ".JAR": File_Extension_Info(".JAR", "Java Jar", [DETAIL_PROGRAM]),

    # Compression Formats
    ".ZIP": File_Extension_Info(".ZIP", "Compressed File", [DETAIL_COMPRESSED]),

    # ROMs
    ".GBA": File_Extension_Info(".GBA", "GBA Rom", [DETAIL_ROM]),
    ".NES": File_Extension_Info(".NES", "NES Rom", [DETAIL_ROM]),
    ".PRG": File_Extension_Info(".PRG", "C64 Rom", [DETAIL_ROM]),

    # Etc.
    "/": File_Extension_Info("/", "", []),
    ".---": File_Extension_Info(".---", "", []),
    ".~~~": File_Extension_Info(".~~~", "", []),
    "._3DSKULL": File_Extension_Info("._3DSKULL", "", []),
    ".ANI": File_Extension_Info(".ANI", "", []),
    ".BIN": File_Extension_Info(".BIN", "", [],),
    ".BSV": File_Extension_Info(".BSV", "", []),
    ".CER": File_Extension_Info(".CER", "", []),
    ".CORRUPT": File_Extension_Info(".CORRUPT", "", []),
    ".CUR": File_Extension_Info(".CUR", "", []),
    ".DB": File_Extension_Info(".DB", "", []),
    ".DLL": File_Extension_Info(".DLL", "", []),
    ".DLM": File_Extension_Info(".DLM", "", []),
    ".DS_STORE": File_Extension_Info(".DS_STORE", "", []),
    ".LNK": File_Extension_Info(".LNK", "", []),
    ".MS": File_Extension_Info(".MS", "", []),  # Weird file in Trash Fleet 3.0
    ".OBJ": File_Extension_Info(".OBJ", "", []),  # pazzt
    ".OZ": File_Extension_Info(".OZ", "", []),
    ".PIF": File_Extension_Info(".PIF", "", []),
    ".SCR": File_Extension_Info(".SCR", "", []),  # BSV2BRD
    ".TRS": File_Extension_Info(".TRS", "", []),
    ".VSP": File_Extension_Info(".VSP", "", []),
    ".WAR": File_Extension_Info(".WAR", "", []),
    ".ZR": File_Extension_Info(".ZR", "", []),
}


def get_detail_suggestions(file_list):
    suggestions = {
        "hints": [],
        "hint_ids": [],
        "unknown_extensions": [],
    }
    for name in file_list:
        ext = os.path.splitext(os.path.basename(name).upper())
        ext = ext[0] if ext[1] == "" else ext[1]

        extension = EXTENSIONS.get(ext)
        if extension:
            suggest = extension.associated_details
            suggestions["hints"].append(
                {"name": name, "type": extension.name, "suggested": suggest, "role": "ambiguous-ext" if extension.ambiguous else "known-ext"}
            )
            suggestions["hint_ids"] += suggest
        else:
            suggestions["hints"].append(
                {"name": name, "type": "Unknown Extension", "role":"unknown-ext"}
            )
            suggestions["unknown_extensions"].append(ext)

    # Get detail names
    qs = Detail.objects.all().values("pk", "title")
    detail_mapping = {}
    for d in qs:
        detail_mapping[d["pk"]] = d["title"]

    suggestions["hint_ids"] = set(suggestions["hint_ids"])
    suggestions["unknown_extensions"] = set(suggestions["unknown_extensions"])
    return suggestions

import math
import os
import re
import tempfile
import zipfile
import urllib.parse

from datetime import datetime, UTC, timedelta

from django.conf import settings
from django.shortcuts import redirect
from django.template.defaultfilters import escape, timeuntil
from django.urls import get_resolver, reverse

from museum_site.constants import DATA_PATH, CHARSET_PATH, HOST
from museum_site.settings import BANNED_IPS

try:
    import zookeeper
    HAS_ZOOKEEPER = True
except ImportError:
    HAS_ZOOKEEPER = False


def calculate_boards_in_zipfile(zip_path):
    if not HAS_ZOOKEEPER:
        return (None, None)
    playable_boards = None
    total_boards = None
    temp_playable = 0
    temp_total = 0

    try:
        zf = zipfile.ZipFile(zip_path)
    except (FileNotFoundError, zipfile.BadZipFile):
        record("Skipping Calculate Boards function due to bad zip")
        return (None, None)

    file_list = zf.namelist()
    tdh = tempfile.TemporaryDirectory(prefix="moz-")
    temp_dir = tdh.name

    for f in file_list:
        name, ext = os.path.splitext(f)
        ext = ext.upper()

        if f.startswith("__MACOSX") or ext != ".ZZT":  # Don't count OSX info directory or non-ZZT files
            continue

        # Extract the file
        try:
            zf.extract(f, path=temp_dir)
        except Exception:
            record("Could not extract {}. Aborting.".format(f))
            return (None, None)

        z = zookeeper.Zookeeper(os.path.join(temp_dir, f))

        to_explore = []
        accessible = []

        # Start with the starting board
        to_explore.append(z.world.current_board)

        false_positives = 0
        for idx in to_explore:
            # Make sure the board idx exists in the file (in case of imported boards with passages)
            if idx >= len(z.boards):
                false_positives += 1
                continue

            # The starting board is clearly accessible
            accessible.append(idx)

            # Get the connected boards via edges
            if (z.boards[idx].board_north != 0 and z.boards[idx].board_north not in to_explore):
                to_explore.append(z.boards[idx].board_north)
            if (z.boards[idx].board_south != 0 and z.boards[idx].board_south not in to_explore):
                to_explore.append(z.boards[idx].board_south)
            if (z.boards[idx].board_east != 0 and z.boards[idx].board_east not in to_explore):
                to_explore.append(z.boards[idx].board_east)
            if (z.boards[idx].board_west != 0 and z.boards[idx].board_west not in to_explore):
                to_explore.append(z.boards[idx].board_west)

            # Get the connected boards via passages
            for stat in z.boards[idx].stats:
                try:
                    stat_name = z.boards[idx].get_element((stat.x, stat.y)).name
                    if stat_name == "Passage":
                        if stat.param3 not in to_explore:
                            to_explore.append(stat.param3)
                except IndexError:
                    # Zookeeper raises this on corrupt boards
                    continue

        # Title screen always counts (but don't count it twice)
        if 0 not in to_explore:
            to_explore.append(0)

        temp_playable += len(to_explore) - false_positives
        temp_total += len(z.boards)

    # Use null instead of 0 to avoid showing up in searches w/ board limits
    playable_boards = None if temp_playable == 0 else temp_playable
    total_boards = None if temp_total == 0 else temp_total
    return (playable_boards, total_boards)


def calculate_release_year(release_date):
    output = None
    if release_date:
        output = datetime(year=release_date.year, month=1, day=1, tzinfo=UTC)
    return output


def calculate_sort_title(string):
    output = ""
    # Handle titles that start with A/An/The
    sort_title = string.lower()

    if sort_title.startswith(("a ", "an ", "the ")):
        sort_title = sort_title[sort_title.find(" ") + 1:]

    # Expand numbers
    digits = 0  # Digits in number
    number = ""  # The actual number
    for idx in range(0, len(sort_title)):
        ch = sort_title[idx]
        if ch in "0123456789":
            digits += 1
            number += ch
            continue
        else:
            if digits == 0:
                output += sort_title[idx]
            else:
                padded_digits = "00000{}".format(number)[-5:]
                output += padded_digits + sort_title[idx]
                digits = 0
                number = ""
    # Finale
    if digits != 0:
        padded_digits = "00000{}".format(number)[-5:]
        output += padded_digits

    return output


def generate_screenshot_from_zip(zip_path, screenshot_path, world=None, board=0, font=None):
    if not HAS_ZOOKEEPER:
        return False

    # Get zip contents
    zf = zipfile.ZipFile(zip_path)

    # Guess the earliest dated world with a ZZT extension
    if world is None:
        all_files = zf.infolist()
        worlds = []
        for f in all_files:
            if (f.filename.lower().endswith(".zzt")):
                worlds.append(f)

        if worlds:
            worlds = sorted(worlds, key=zipinfo_datetime_tuple_to_str)
            world = worlds[0].filename

    if world is None:
        return False

    # Extract the file and render
    try:
        zf.extract(world, path=DATA_PATH)
    except (NotImplementedError, KeyError):
        return False
    zk = zookeeper.Zookeeper(os.path.join(DATA_PATH, world))
    zk.boards[board].screenshot(os.path.join(screenshot_path[:-4]), title_screen=(not bool(board)))

    # Delete the extracted world
    # TODO: This leaves lingering folders for zips in folders
    os.remove(os.path.join(DATA_PATH, world))

    return True


def get_letter_from_title(title):
    """ Returns the letter a zfile should be listed under after removing (a/an/the) from the provided title """
    title = title.lower()
    for eng_article in ["a ", "an ", "the "]:
        if title.startswith(eng_article):
            title = title.replace(eng_article, "", 1)

    return title[0] if title[0] in "abcdefghijklmnopqrstuvwxyz" else "1"


def legacy_redirect(request, name=None, *args, **kwargs):
    # Strip arguments if they're no longer needed
    if "strip" in kwargs:
        for stripped_arg in kwargs["strip"]:
            kwargs.pop(stripped_arg)
        kwargs.pop("strip")

    if kwargs.get("detail_slug"):  # /detail/view/<slug>/ to /file/browse/detail/<slug>
        url = reverse("zfile_browse_field", kwargs={"field": "detail", "value": kwargs["detail_slug"]})
    elif kwargs.get("genre_slug"):  # /genre/<slug>/ to /file/browse/genre/<slug>
        url = reverse("zfile_browse_field", kwargs={"field": "genre", "value": kwargs["genre_slug"]})
    else:
        url = reverse(name, args=args, kwargs=kwargs)

    if request.META["QUERY_STRING"]:
        url += "?" + request.META["QUERY_STRING"]

    return redirect(url, permanent=True)


def extract_file_key_from_url(url):
    url = urllib.parse.urlparse(url)
    path = url.path

    # Strip slashes before splitting
    if path.startswith("/"):
        path = path[1:]
    if path.endswith("/"):
        path = path[:-1]

    path = path.split("/")

    if path[0] != "file":
        return None

    if len(path) >= 3:
        return path[2]
    else:
        return None


def env_from_host(host):
    envs = {"beta.museumofzzt.com": "BETA", "museumofzzt.com": "PROD", "www.museumofzzt.com": "PROD"}
    return envs.get(host, "DEV")


def throttle_check(request, attempt_name, expiration_name, max_attempts, lockout_mins=5):
    """ This function was used for account resets and no longer seems to be implemented """
    # Origin time for calculating lockout
    now = datetime.now(UTC)

    # Increment attempts
    request.session[attempt_name] = request.session.get(attempt_name, 0) + 1

    # Lockout after <max_attempts>
    if request.session[attempt_name] > max_attempts:
        # If they're already locked out and the timer's expired, resume
        if (
            request.session.get(expiration_name) and
            (str(now)[:19] > request.session[expiration_name])
        ):
            request.session[attempt_name] = 1
            del request.session[attempt_name]
            del request.session[expiration_name]
            return True

        # Otherwise lock them out
        delta = timedelta(minutes=lockout_mins)
        request.session[expiration_name] = str(now + delta)
        return False
    return True


def profanity_filter(text):
    PROFANITY = [
        'ergneq', 'snttbg', 'shpx', 'fuvg', 'qnza', 'nff', 'cvff', 'phag', 'avttre', 'ovgpu'
    ]
    output = []
    words = text.split(" ")
    for word in words:
        for p in PROFANITY:
            pword = codecs.encode(p, "rot_13")
            if word.lower().find(pword) != -1:
                replacement = ("✖" * len(pword))
                word = word.lower().replace(pword, replacement)
        output.append(word)

    return " ".join(output)


def banned_ip(ip):
    if ip in BANNED_IPS:
        return True
    elif "." in ip:
        ip = ".".join(ip.split(".")[:-1]) + ".*"
        if ip in BANNED_IPS:
            return True
        return False


def zipinfo_datetime_tuple_to_str(raw):
    dt = raw.date_time
    y = str(dt[0])
    m = str(dt[1]).zfill(2)
    d = str(dt[2]).zfill(2)
    h = str(dt[3]).zfill(2)
    mi = str(dt[4]).zfill(2)
    s = str(dt[5]).zfill(2)
    out = "{}-{}-{} {}:{}:{}".format(y, m, d, h, mi, s)
    return out


def record(*args, **kwargs):
    if settings.ENVIRONMENT != "PROD":
        print(*args, **kwargs)  # Non-Debug print


def zookeeper_init(*args, **kwargs):
    if not HAS_ZOOKEEPER:
        return False

    z = zookeeper.Zookeeper(*args, **kwargs)
    return z


def zookeeper_extract_font(font_filename, font_id, charset_name):
    if not HAS_ZOOKEEPER:
        return False

    z = zookeeper.Zookeeper()
    z.export_font(os.path.join(DATA_PATH, font_filename), os.path.join(CHARSET_PATH, "{}-{}.png".format(font_id, charset_name)), 1)


def get_all_tool_urls(zfile=None, ignored_url_names=[], audit_pages=None):
    output = {"Auditing":[], "General Tools":[], "zfile_tools":[]}
    """ Atrocious variable names """
    url_patterns = get_resolver().url_patterns
    for p in url_patterns:
        if p.pattern.describe() == "''":  # Base path for urls
            urls = p
            break

    url_list = urls.url_patterns

    """ Normalcy """
    for u in url_list:
        url_str = str(u.pattern)
        if ((not url_str.startswith("tools")) or (u.name in ignored_url_names)):
            continue

        if "audit" in url_str:
            bucket = output["Auditing"]
        elif "<str:key>" in url_str:
            bucket = output["zfile_tools"]
        else:
            bucket = output["General Tools"]

        url_info = {"url_name": u.name, "text": u.name.replace("_", " ").replace("tool ", "").title()}
        bucket.append(url_info)

    if audit_pages:
        for k, v in audit_pages.items():
            url_info = {"url": "/tools/audit/" + k + "/", "text": v["title"]}
            output["Auditing"].append(url_info)

    for k, v in output.items():
        output[k] = sorted(output[k], key=lambda s: s["text"])
    return output


def cheat_prompt_check(request):
    cheat = request.GET.get("q")
    applied_cheat = None
    if not cheat:
        return None

    cheat = cheat.upper()
    if cheat == "+DEBUG":
        applied_cheat = cheat
        request.session["DEBUG"] = 1
    elif cheat == "-DEBUG":
        applied_cheat = cheat
        if request.session.get("DEBUG"):
            del request.session["DEBUG"]
    elif cheat == "+BETA":
        applied_cheat = cheat
        request.session["TEMP_FILE_VIEWER_BETA"] = 1
    elif cheat == "-BETA":
        applied_cheat = cheat
        if request.session.get("TEMP_FILE_VIEWER_BETA"):
            del request.session["TEMP_FILE_VIEWER_BETA"]
    return applied_cheat


MUSEUM_BOOKMARKS = {
    "weave": "https://meangirls.itch.io/weave-4",
}

class Meta_Tag_Block():
    tags = {
        "url": "<meta property='og:url' content='{}'>\n",
        "title": "<meta property='og:title' content='{}'>\n",
        "image": "<meta property='og:image' content='{}'>\n",
        "description": "<meta name='description' content='{}'>\n",
        "author": "<meta name='author' content='{}'>\n",
        "og:type": "<meta property='og:type' content='{}'>\n",
    }

    def __init__(self, url="", title="", image="", description="", author="Dr. Dos", og_type="website"):
        self.set_url(url)
        self.set_title(title)
        self.set_image(image)
        self.set_description(description)
        self.set_author(author)
        self.set_og_type(og_type)

    def set_url(self, url):
        if url.startswith("/"):
            url = url[1:]
        self.url = (HOST + url) if url else HOST

    def set_title(self, title):
        self.title = (title + " - Museum of ZZT") if title else "Museum of ZZT"

    def set_image(self, image):
        if not image:
            self.image = ""
            return False
        if not image.startswith("/static/"):
            if image.startswith("/"):
                image = image[1:]
            image = "static/" + image
        self.image =  (HOST + image) if image else ""

    def set_description(self, description):
        self.description = description

    def set_author(self, author):
        self.author = author

    def set_og_type(self, og_type):
        self.og_type = og_type

    def __str__(self):
        return self.render()

    def render(self):
        output = ""
        output += self.tags["url"].format(self.url) if self.url else ""
        output += self.tags["title"].format(escape(self.title)) if self.title else ""
        output += self.tags["image"].format(escape(self.image)) if self.image else ""
        output += self.tags["description"].format(escape(self.description)) if self.description else ""
        output += self.tags["author"].format(escape(self.author)) if self.author else ""
        output += self.tags["og:type"].format(self.og_type) if self.og_type else ""
        return output


def get_frontpage_events(qs):
    if False:  # Manual front page event
        main_event = {"title": "Oktrollberfest 2025", "image": "/static/images/oktroll-2025-goose.png", "when": "Through Oct. 31st", "when_title": "", "url": "https://itch.io/jam/oktrollberfest-2025"}
    else:
        # Obtain events
        now = datetime.now(UTC)
        cutoff = now + timedelta(hours=-1)
        events = list(qs.filter(visible=True, when__gte=cutoff).order_by("when"))
        if events:
            until = timeuntil(events[0].when)

        main_event = None
        if events:
            title = "Livestream - " + events[0].title
            when = "In " + until.split(",")[0]
            if str(now)[:10] >= str(events[0].when)[:10]:
                when = "Right now!"
            when_title = str(events[0].when)[:19] + " UTC"
            url = "https://twitch.tv/worldsofzzt/"
            image = events[0].preview_image

            main_event = {"title": title, "image": image, "when": when, "when_title": when_title, "url": url}
    return main_event

def get_ascii_table_data():
    table_data = []
    characters = " ☺☻♥♦♣♠•◘○◙♂♀♪♫☼►◄↕‼¶§▬↨↑↓→←∟↔▲▼ !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~⌂ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜ¢£¥₧ƒáíóúñÑªº¿⌐¬½¼¡«»░▒▓│┤╡╢╖╕╣║╗╝╜╛┐└┴┬├─┼╞╟╚╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌█▄▌▐▀αßΓπΣσµτΦΘΩδ∞φε∩≡±≥≤⌠⌡÷≈°∙·√ⁿ²■ "
    for idx in range(0, 256):
        x_offset = 32
        y_offset = 28
        table_data.append({"idx": idx, "number": str(idx).zfill(3), "char": characters[idx], "name": "Foob", "x_offset": x_offset, "y_offset": y_offset})
    return table_data

def get_color_table_data():
    palette_lo = []
    palette_hi = []
    color_css_names = ["black", "darkblue", "darkgreen", "darkcyan", "darkred", "darkpurple", "darkyellow", "gray", "darkgray", "blue", "green", "cyan", "red", "purple", "yellow", "white", "???"]

    for idx in range(0, 128):
        color = {"idx": idx, "fg": color_css_names[idx % 16], "bg": color_css_names[idx // 16]}
        palette_lo.append(color)
        color = {"idx": idx + 128, "fg": color_css_names[(idx + 128) % 16], "bg": color_css_names[(idx + 128) // 16]}
        palette_hi.append(color)

    return (palette_lo, palette_hi)

def list_to_columns(category, data_list):
    # Break the list of results into 4 columns
    if category != "year":
        data_list = sorted(data_list, key=lambda s: re.sub(r'(\W|_)', "é", s.title.lower()))

    # Split the list into 4 sets
    column_length = math.ceil(len(data_list) / 4)
    wip_columns = []
    for idx in range(0, 4):
        wip_columns.append(data_list[:column_length])
        data_list = data_list[column_length:]

    # Add headings to create final columns
    final_columns = [[], [], [], []]
    observed_letters = []
    last_letter = ""
    force_header = False
    for idx in range(0, 4):
        wip_column = wip_columns[idx]
        if idx != 0:
            force_header = True

        if category != "year":
            for entry in wip_column:
                first_letter = entry.title[0].upper()
                if first_letter in "1234567890":
                    first_letter = "#"
                elif first_letter not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    first_letter = "*"
                if (first_letter not in observed_letters) or force_header:
                    observed_letters.append(first_letter)
                    final_columns[idx].append({"kind": "header", "title": first_letter + (" (cntd.)" if force_header else "")})
                    force_header = False

                final_columns[idx].append({"url": entry.get_absolute_url(), "title": entry.title, "kind": "entry"})
            # Mark letters repeated between columns
            last_letter = first_letter
        else:
            for entry in wip_column:
                entry_name = entry
                if entry == "unk":
                    entry_name = "Unknown"
                final_columns[idx].append({"url": reverse("zfile_browse_field", kwargs={"field": "year", "value": entry}), "title": entry_name, "kind": "entry"})
    return final_columns

def get_patron_supporters(patrons):
    # Hardcoded credits
    unregistered_supporters_file = os.environ.get("MOZ_UNREGISTERED_SUPPORTERS_FILE", None)
    supporters = []
    bigger_supporters = []
    biggest_supporters = []
    hc_emails = []
    bigger_hc_emails = []
    biggest_hc_emails = []

    if unregistered_supporters_file is not None and os.path.isfile(unregistered_supporters_file):
        with open(unregistered_supporters_file) as fh:
            raw = json.loads(fh.read())

        for row in raw:
            if row.get("pledge") == "biggest":
                biggest_supporters.append(row)
            elif row.get("pledge") == "bigger":
                bigger_supporters.append(row)
            else:
                supporters.append(row)

        # Emails to reference
        for row in supporters:
            hc_emails.append(row["email"])
        for row in bigger_supporters:
            bigger_hc_emails.append(row["email"])
        for row in biggest_supporters:
            biggest_hc_emails.append(row["email"])
    else:
        supporters = []
        bigger_supporters = []
        biggest_supporters = []

    # Get users known to be patrons
    no_longer_hardcoded = []
    for p in patrons:
        if p.site_credits_name:
            info = {"name": p.site_credits_name, "char": p.char, "fg": p.fg, "bg": p.bg, "img": "blank-portrait.png", "email": p.patron_email}

            if p.patron_email in hc_emails:
                idx = hc_emails.index(p.patron_email)
                hc_emails[idx] = info
                no_longer_hardcoded.append(p.patron_email)
                continue
            elif p.patron_email in bigger_hc_emails:
                idx = bigger_hc_emails.index(p.patron_email)
                bigger_hc_emails[idx] = info
                no_longer_hardcoded.append(p.patron_email)
                continue
            elif p.patron_email in biggest_hc_emails:
                idx = biggest_hc_emails.index(p.patron_email)
                biggest_hc_emails[idx] = info
                no_longer_hardcoded.append(p.patron_email)
                continue

            if p.patronage >= 10000:
                biggest_supporters.append(info)
            elif p.patronage >= 2000:
                bigger_supporters.append(info)
            else:
                supporters.append(info)

    supporters.sort(key=lambda k: k["name"].lower())
    bigger_supporters.sort(key=lambda k: k["name"].lower())
    biggest_supporters.sort(key=lambda k: k["name"].lower())

    # Pad out entries to look cleaner
    while len(bigger_supporters) % 3 != 0:
        bigger_supporters.append({"name": "ZZZZZZZZZZSTUB", "email": "STUB"})
    while len(biggest_supporters) % 2 != 0:
        biggest_supporters.append({"name": "ZZZZZZZZZZSTUB", "email": "STUB"})
    while len(supporters) % 3 != 0:
        supporters.append({"name": "ZZZZZZZZZZSTUB", "email": "STUB"})
    return (supporters, bigger_supporters, biggest_supporters)

def zeta_get_szzt_world(zeta_config, zfile):
    szzt_world = ""
    zip_file = zipfile.ZipFile(os.path.join(zfile.phys_path()))
    files = zip_file.namelist()
    for f in files:
        basename = os.path.basename(f)
        if f.lower().endswith(".szt") and basename == f:
            szzt_world = f
            break
    return zeta_config.arguments.replace("{SZZT_WORLD}", szzt_world)

def zeta_get_font_file():
    return True

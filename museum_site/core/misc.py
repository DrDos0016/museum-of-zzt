import os
import zipfile
import urllib.parse

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

from museum_site.constants import BANNED_IPS, TEMP_PATH

try:
    import zookeeper
    HAS_ZOOKEEPER = True
except ImportError:
    HAS_ZOOKEEPER = False


def calculate_boards_in_zipfile(zip_path):
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

    for f in file_list:
        name, ext = os.path.splitext(f)
        ext = ext.upper()

        if f.startswith("__MACOSX") or ext != ".ZZT":  # Don't count OSX info directory or non-ZZT files
            continue

        # Extract the file
        try:
            zf.extract(f, path=TEMP_PATH)
        except Exception:
            record("Could not extract {}. Aborting.".format(f))
            return (None, None)

        z = zookeeper.Zookeeper(os.path.join(TEMP_PATH, f))

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

        # Delete the extracted file from the temp folder
        os.remove(os.path.join(TEMP_PATH, f))

    # Use null instead of 0 to avoid showing up in searches w/ board limits
    playable_boards = None if temp_playable == 0 else temp_playable
    total_boards = None if temp_total == 0 else temp_total
    return (playable_boards, total_boards)

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
        url = reverse("browse_field", kwargs={"field":"detail", "value":kwargs["detail_slug"]})
    elif kwargs.get("genre_slug"):  # /genre/<slug>/ to /file/browse/genre/<slug>
        url = reverse("browse_field", kwargs={"field":"genre", "value":kwargs["genre_slug"]})
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
    if host in ["beta.museumofzzt.com"]:
        return "BETA"
    elif host in ["museumofzzt.com", "www.museumofzzt.com"]:
        return "PROD"
    else:
        return "DEV"


def throttle_check(request, attempt_name, expiration_name, max_attempts, lockout_mins=5):
    """ This function was used for account resets and no longer seems to be implemented """
    # Origin time for calculating lockout
    now = datetime.now()

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
        print(*args, **kwargs)

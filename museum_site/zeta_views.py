import json
import os
import zipfile

from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import render, redirect

from museum_site.constants import STATIC_PATH, ZETA_EXECUTABLES
from museum_site.core.decorators import rusty_key_check
from museum_site.core.detail_identifiers import *
from museum_site.core.image_utils import crop_file, optimize_image, IMAGE_CROP_PRESETS, open_base64_image
from museum_site.core.redirects import explicit_redirect_check
from museum_site.core.zeta_identifiers import *
from museum_site.models import File as ZFile
from museum_site.models import Zeta_Config


@rusty_key_check
def zeta_launcher(request, key=None, components=["controls", "instructions", "credits", "advanced", "players"]):
    data = {"title": "Zeta Launcher"}

    PLAY_METHODS = {"archive": {"name": "Archive.org - DosBox Embed"}, "zeta": {"name": "Zeta"}}

    # Template rendering mode
    # full - Extends "world.html", has a file header
    # popout - Extends "play-popout.html", removes all site components
    data["mode"] = request.GET.get("mode", "full")
    data["base"] = "museum_site/main.html"

    # Determine visible components
    data["components"] = {
        "controls": True if "controls" in components else False,
        "instructions": True if "instructions" in components else False,
        "credits": True if "credits" in components else False,
        "advanced": True if "advanced" in components else False,
        "players": True if "players" in components else False,
    }

    # Show advanced settings if requested in URL
    if request.GET.get("advanced"):
        data["components"]["advanced"] = True

    # Hide everything in popout mode and force Zeta
    if data["mode"] == "popout":
        data["base"] = "museum_site/play-popout.html"
        data["components"] = {
            "controls": False,
            "instructions": False,
            "credits": False,
            "advanced": False,
            "players": False,
        }
        player = "zeta"

    if data["components"]["advanced"]:
        # data["charsets"] = CUSTOM_CHARSET_LIST
        data["all_files"] = ZFile.objects.zeta_compatible().order_by("sort_title", "id").only("id", "title")

    data["charset_override"] = request.GET.get("charset_override", "")
    data["executable"] = request.GET.get("executable", "AUTO")
    data["engine"] = data["executable"]
    data["ZETA_EXECUTABLES"] = ZETA_EXECUTABLES

    # Get files requested
    if key and key != "LOCAL":
        data["file"] = ZFile.objects.filter(key=key).first()
        data["local"] = False
    else:
        data["file"] = None  # This will be the "prime" file
        data["local"] = True

    # Itch games get listed as an option
    if data["file"].itch_dl:
        PLAY_METHODS["itch"] = {"name": "Play On Itch.io - Leave Museum"}

    data["file_ids"] = list(map(int, request.GET.getlist("file_id")))

    # HOTFIXES (BINB)
    data["HOTFIX"] = "true" if data["file"].pk in [3089, 3527] else "false"

    if (data["file"] and data["file"].id not in data["file_ids"]):
        data["file_ids"] = [data["file"].id] + data["file_ids"]

    data["file_count"] = len(data["file_ids"])
    data["included_files"] = []
    for f in ZFile.objects.filter(pk__in=data["file_ids"]):
        data["included_files"].append(f.download_url())
        if data["file"] is None:
            data["file"] = f

    # Check for explicit flag/permissions
    if data["file"] and data["file"].explicit:
        check = explicit_redirect_check(request, data["file"].pk)
        if check != "NO-REDIRECT":
            return check

    # Set the page title
    if data["file"]:
        data["title"] = data["file"].title + " - Play Online"

    if len(data["included_files"]) == 1:  # Use the file ID for the SaveDB
        data["zeta_database"] = f.id

    if data["components"]["players"]:
        # Find supported play methods
        all_play_methods = list(PLAY_METHODS.keys())
        compatible_players = []

        if "zeta" in all_play_methods:
            if data["file"] and data["file"].supports_zeta_player():
                compatible_players.append("zeta")

                # For unpublished worlds, assume yes but add a disclaimer
                if data["file"].is_detail(DETAIL_UPLOADED):
                    data["unpublished"] = True

        if "archive" in all_play_methods:
            if data["file"] and data["file"].archive_name:
                compatible_players.append("archive")

        if "itch" in all_play_methods:
            compatible_players.append("itch")

        # Is there a manually selected preferred player?
        if (request.GET.get("player") and request.GET.get("player") in all_play_methods):
            preferred_player = request.GET.get("player")
        else:  # If not, use Zeta as the default player
            preferred_player = "zeta"

        # Does the preferred player support this file?
        if preferred_player in compatible_players:
            player = preferred_player
        else:  # If not, force this hierarchy
            if "zeta" in compatible_players:
                player = "zeta"
            elif "itch" in compatible_players:
                player = "itch"
            elif "archive" in compatible_players:
                player = "archive"
            else:
                player = "none"

        # Finalize the player
        data["player"] = player

        # Leave to Itch is needed
        if player == "itch":
            return redirect(data["file"].itch_dl.url)

        # Populate options for any alternative players
        data["players"] = {}
        for option in compatible_players:
            data["players"][option] = PLAY_METHODS[option]

    # Get info for all Zeta configs if needed
    if data["components"]["advanced"]:
        data["config_list"] = Zeta_Config.objects.exclude(pk=ZETA_RESTRICTED).only("id", "name")

    # Get Zeta Config for file
    data["zeta_config"] = data["file"].zeta_config if data["file"] else None
    if request.GET.get("zeta_config"):  # User override
        data["zeta_config"] = Zeta_Config.objects.get(pk=int(request.GET["zeta_config"]))

    # Override config with user requested options
    if data["zeta_config"]:
        data["zeta_config"].user_configure(request.GET)
    else:
        data["zeta_config"] = Zeta_Config.objects.get(pk=ZETA_ZZT32R)

    # Extra work for custom fonts
    if data["zeta_config"].name.startswith("Custom Font - "):
        generic_font = ""
        zip_file = zipfile.ZipFile(os.path.join(data["file"].phys_path()))
        files = zip_file.namelist()
        font_type = "NONE"
        for f in files:
            if f.lower().endswith(".com"):
                generic_font = f
                font_type = ".COM"
            elif f.lower().endswith(".chr"):
                generic_font = f
                font_type = ".CHR"

        if font_type == ".COM":
            data["zeta_config"].commands = (data["zeta_config"].commands.replace("{font_file}", generic_font))
        elif font_type == ".CHR":
            data["zeta_config"].commands = []
            data["zeta_config"].engine = json.dumps({
                "charset": generic_font,
                "lock_charset": True,
            })


    # Extra work for custom EXE
    if data["zeta_config"].name.startswith("Use Included EXE"):
        generic_exe = ""
        zip_file = zipfile.ZipFile(os.path.join(data["file"].phys_path()))
        files = zip_file.namelist()
        for f in files:
            basename = os.path.basename(f)
            if f.lower().endswith(".exe") and basename == f:
                generic_exe = f
            # Prioritize these two
            if f.lower() in ["zzt.exe", "superz.exe"] or (f.lower().startswith("weave") and f.lower().endswith("exe")):
                break
        data["zeta_config"].commands = data["zeta_config"].commands.replace("{executable_file}", generic_exe)

    # Override for "Live" Zeta edits
    if request.GET.get("live"):
        data["zeta_live"] = True
        data["zeta_url"] = "/zeta-live?pk={}&world={}&start={}".format(data["file"].id, request.GET.get("world"), request.GET.get("start", 0))
        data["zeta_config"].arguments = request.GET.get("world", "")
    elif request.GET.get("discord"):
        data["zeta_url"] = "/zeta-live?discord=1&world={}".format(request.GET.get("world"))

    # Set default scale
    data["zeta_player_scale"] = int(request.COOKIES.get("zeta_player_scale", 1))

    # Adjust canvas size if Super ZZT
    data["zeta_config"].base_width = 640
    data["zeta_config"].base_height = 350

    if data["file"] and data["file"].is_detail(DETAIL_SZZT):
        data["zeta_config"].base_height = 400

    if data["local"]:
        player = "zeta_local"

    # Is this lone ZFile yours and unpublished?
    if data["file_count"] == 1 and data["file"].is_detail(DETAIL_UPLOADED) and request.user.is_authenticated:
        if data["file"].upload.user and data["file"].upload.user.pk == request.user.pk:
            data["your_upload"] = True

            if request.method == "POST":
                image = open_base64_image(request.POST.get("b64img"))
                image = image.crop(IMAGE_CROP_PRESETS["ZZT"])
                image_path = os.path.join(STATIC_PATH, "screenshots/{}/{}.png".format(data["file"].bucket(), data["file"].key))
                image.save(image_path)
                data["file"].has_preview_image = True
                data["file"].save()
                data["screenshot_updated"] = True

    return render(request, "museum_site/play_{}.html".format(player), data)


def zeta_live(request):
    if request.GET.get("discord"):
        with open("/var/projects/museum/museum_site/static/data/discord-zzt/" + request.GET.get("filename"), "rb") as fh:
            response = HttpResponse(content_type="application/octet-stream")
            response["Content-Disposition"] = "attachment; filename=DISCORD.ZIP"
            response.write(fh.read())
        return response

    pk = int(request.GET["pk"])
    fname = request.GET["world"]
    start = int(request.GET["start"]).to_bytes(1, byteorder="little")

    f = ZFile.objects.get(pk=int(pk))

    # Open original zip and extract the file
    with zipfile.ZipFile(f.phys_path()) as orig_zip:
        orig_file = orig_zip.read(fname)

    # Adjust starting board
    modded_file = orig_file[:17] + start + orig_file[18:]

    # Extract the file
    # Adjust the file

    # Return it to Zeta
    temp_zip = BytesIO()

    # Create new zip
    with zipfile.ZipFile(temp_zip, "w") as mem_zip:
        # Using the basename of the filepath within the zip allows playing
        # something in a folder. It's hacky, but works.
        mem_zip.writestr(os.path.basename(fname), modded_file)

    response = HttpResponse(content_type="application/octet-stream")
    response["Content-Disposition"] = "attachment; filename=TEST.ZIP"
    response.write(temp_zip.getvalue())
    return response

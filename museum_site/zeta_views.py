from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from .common import *
from .constants import *
from .models import *


def zeta_launcher(request, letter=None, filename=None, components=["controls", "instructions", "credits", "advanced", "players"]):
    data = {"title": "Zeta Launcher"}
    # Template rendering mode
    # full - Extends "world.html", has a file header
    # popout - Extends "play-popout.html", removes all site components
    data["mode"] = request.GET.get("mode", "full")
    data["base"] = "museum_site/world.html"

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
        #data["charsets"] = CUSTOM_CHARSET_LIST
        data["all_files"] = File.objects.filter(
            details__id__in=[DETAIL_ZZT, DETAIL_SZZT, DETAIL_UPLOADED]
        ).order_by("sort_title", "id").only("id", "title")

    data["charset_override"] = request.GET.get("charset_override", "")
    data["executable"] = request.GET.get("executable", "AUTO")
    data["engine"] = data["executable"]
    data["ZETA_EXECUTABLES"] = ZETA_EXECUTABLES

    # Get files requested
    if letter and filename:
        data["file"] = File.objects.get(letter=letter, filename=filename)
    else:
        data["file"] = None  # This will be the "prime" file

    data["file_ids"] = list(map(int, request.GET.getlist("file_id")))

    if (data["file"] and data["file"].id not in data["file_ids"]):
        data["file_ids"] = [data["file"].id] + data["file_ids"]

    data["file_count"] = len(data["file_ids"])
    data["included_files"] = []
    for f in File.objects.filter(pk__in=data["file_ids"]):
        data["included_files"].append(f.download_url())
        if data["file"] is None:
            data["file"] = f

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
            if data["file"].supports_zeta_player():
                compatible_players.append("zeta")
            elif data["file"].is_uploaded():
                # For unpublished worlds, assume yes but add a disclaimer
                compatible_players.append("zeta")
                data["unpublished"] = True

        if "archive" in all_play_methods:
            if data["file"].archive_name:
                compatible_players.append("archive")

        # Is there a manually selected preferred player?
        if request.GET.get("player") and request.GET.get("player") in all_play_methods:
            preferred_player = request.GET.get("player")
        else:  # If not, use Zeta as the default player
            preferred_player = "zeta"

        # Does the preferred player support this file?
        if preferred_player in compatible_players:
            player = preferred_player
        else:  # If not, force this hierarchy
            if "zeta" in compatible_players:
                player = "zeta"
            elif "archive" in compatible_players:
                player = "archive"
            else:
                player = "none"

        # Finalize the player
        data["player"] = player

        # Populate options for any alternative players
        data["players"] = {}
        for option in compatible_players:
            data["players"][option] = PLAY_METHODS[option]

    # Get info for all Zeta configs if needed
    if data["components"]["advanced"]:
        data["config_list"] = Zeta_Config.objects.only("id", "name")

    # Get Zeta Config for file
    data["zeta_config"] = data["file"].zeta_config
    if request.GET.get("zeta_config"):  # User override
        data["zeta_config"] = Zeta_Config.objects.get(pk=int(request.GET["zeta_config"]))

    # Override config with user requested options
    if data["zeta_config"]:
        data["zeta_config"].user_configure(request.GET)
    else:
        data["zeta_config"] = Zeta_Config.objects.get(pk=1)  # TODO make this a constant

    # Extra work for custom fonts
    if data["zeta_config"].name.startswith("Custom Font - Generic"):
        generic_font = ""
        zip_file = zipfile.ZipFile(os.path.join(data["file"].phys_path()))
        files = zip_file.namelist()
        for f in files:
            if f.lower().endswith(".com"):
                generic_font = f
        data["zeta_config"].commands = data["zeta_config"].commands.replace("{font_file}", generic_font)

    # Override for "Live" Zeta edits
    if request.GET.get("live"):
        data["zeta_live"] = True
        data["zeta_url"] = "/zeta-live?pk={}&world={}&start={}".format(
            data["file"].id,
            request.GET.get("world"),
            request.GET.get("start", 0)
        )
    elif request.GET.get("discord"):
        data["zeta_url"] = "/zeta-live?discord=1&world={}".format(
            request.GET.get("world")
        )

    # Set default scale
    data["zeta_player_scale"] = int(request.COOKIES.get("zeta_player_scale", 1))
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

    f = File.objects.get(pk=int(pk))

    temp_bytes = BytesIO()

    # Open original zip and extract the file
    with zipfile.ZipFile(f.phys_path()) as orig_zip:
        orig_file = orig_zip.read(fname)

    # Adjust starting board
    modded_file = orig_file[:17] + start + orig_file[18:]

    # temp_bytes.write(orig_file)

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


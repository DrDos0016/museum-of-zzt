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
from museum_site.core.misc import Meta_Tag_Block
from museum_site.core.redirects import explicit_redirect_check
from museum_site.core.zeta_identifiers import *
from museum_site.models import File as ZFile
from museum_site.models import Collection, Article, Zeta_Config
from museum_site.views import Museum_Base_Template_View


class Zeta_Launcher_View(Museum_Base_Template_View):
    title = "Zeta Launcher"  # Default title
    template_name = "museum_site/ascii-reference.html"

    POSSIBLE_COMPONENTS = ["controls", "instructions", "credits", "advanced", "players"]

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        print(kwargs)
        self.components = {"controls": True, "instructions": True, "credits": True, "advanced": False, "players": True}
        self.key = kwargs.get("key")
        self.mode = request.GET.get("mode") or "full"
        self.base_template = "museum_site/play-popout.html" if (self.mode == "popout") else "museum_site/main.html"
        self.local_file = (self.key == "LOCAL")
        self.redirect_to = None

    def get_template_names(self):
        return "museum_site/play_zeta.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["base"] = self.base_template
        context["ZETA_EXECUTABLES"] = ZETA_EXECUTABLES
        context["charset_override"] = self.request.GET.get("charset_override", "")
        context["executable"] = self.request.GET.get("executable", "AUTO")
        context["engine"] = context["executable"]  # TODO Why is this a duplicate
        context["components"] = self.get_visible_components()
        if context["components"]["advanced"]:
            context["all_files"] = ZFile.objects.zeta_compatible().order_by("sort_title", "id").only("id", "title")

        zfile_ids = list(map(int, self.request.GET.getlist("file_id")))
        (context["zfile"], context["all_zfiles"], context["included_files"]) = self.get_zfiles(zfile_ids)
        context["file_count"] = len(zfile_ids)

        self.redirect_to = self.check_for_explicit_redirect(context["zfile"])

        context["player_methods"] = self.get_player_methods(context["zfile"])  # TODO?

        context["title"] = (context["zfile"].title + " - Play Online") if context["zfile"] else Zeta_Launcher_View.title
        context["zeta_database"] = context["all_zfiles"][0].pk if len(context["all_zfiles"]) == 1 else "generic-zeta-save-db"

        if context["components"]["players"]:
            (context["player"], context["players"]) = self.get_play_method(context["zfile"], context["player_methods"], self.request.GET.get("player"))

        if context["components"]["advanced"]:
            context["config_list"] = Zeta_Config.objects.exclude(pk=ZETA_RESTRICTED).only("id", "name")

        context["zeta_config"] = self.get_zeta_config(context["zfile"])
        # TODO "Extra Work" stuff

        # Set default scale
        context["zeta_player_scale"] = int(self.request.COOKIES.get("zeta_player_scale", 1))

        # Determine initial canvas size for ZZT/SZZT
        (context["zeta_config"].base_width, context["zeta_config"].base_height) = (640, 350)
        if context["zfile"] and context["zfile"].is_detail(DETAIL_SZZT):
            context["zeta_config"].base_height = 400

        #if data["local"]:  # TODO IS THIS IMPLEMENTED?
            #player = "zeta_local"
        context["file"] = context["zfile"]  # TODO: Hotfix for compatibility w/ current template
        print("Players?", context["players"])
        print("PLAYER", context["player"])
        return context

    def get_visible_components(self):
        components = {}
        components.update(self.components)
        components["advanced"] = bool(self.request.GET.get("advanced"))
        print("Vis Components", components)
        return components

    def get_zeta_compatible_zfiles(self):
            return ZFile.objects.zeta_compatible().order_by("sort_title", "id").only("id", "title")

    def get_zfiles(self, zfile_ids):
        primary_zfile = None
        all_included_zfiles = []
        zfile_urls = []

        if self.key:
            primary_zfile = ZFile.objects.filter(key=self.key).first()
        if (primary_zfile and primary_zfile.id not in zfile_ids):
            zfile_ids = [primary_zfile.id] + zfile_ids

        for zf in ZFile.objects.filter(pk__in=zfile_ids):
            all_included_zfiles.append(zf)
            zfile_urls.append(zf.download_url())

        if primary_zfile is None and all_included_zfiles:
            primary_zfile = included_zfiles[0]

        print("ZFILES ARE", primary_zfile, all_included_zfiles)

        return (primary_zfile, all_included_zfiles, zfile_urls)

    def get_player_methods(self, zfile):
        play_methods = {"archive": {"name": "DosBox - Internet Archive Embed"}, "zeta": {"name": "Zeta - Museum of ZZT Hosted"}}
        if zfile and zfile.itch_dl:
            play_methods["itch"] = {"name": "Play On Itch.io - Leave Museum"}
        return play_methods

    def get_play_method(self, zfile, play_methods, user_requested_player):
        # Determine play methods available and play method to use
        all_play_methods = list(play_methods.keys())
        print("all", all_play_methods)
        compatible_players = []
        unpublished = True if (zfile and zfile.is_detail(DETAIL_UPLOADED) )else False

        if "zeta" in all_play_methods and zfile and zfile.supports_zeta_player:
            compatible_players.append("zeta")
        if "archive" in all_play_methods and zfile and zfile.archive_name:
            compatible_players.append("archive")
        if "itch" in all_play_methods:
            compatible_players.append("itch")

        preferred_player = user_requested_player if (user_requested_player in all_play_methods) else "zeta"

        # Use the preferred player, or the earliest compatible player in this list
        player = "none"
        for potential_player in [preferred_player, "zeta", "itch", "archive"]:
            if potential_player in compatible_players:
                player = potential_player
                break

        # Populate options for any alternative players
        #data["players"] = {}
        #for option in compatible_players:
        #    data["players"][option] = PLAY_METHODS[option]

        if player == "itch":  # Itch needs a redirect
            self.redirect_to = zfile.itch_dl.url

        return (player, play_methods)

    def check_for_explicit_redirect(self, zfile):
        if zfile and zfile.explicit:
            check = explicit_redirect_check(self.request, zfile.pk)
            if check != "NO-REDIRECT":
                return check
        return None

    def get_zeta_config(self, zfile):
        # Get Zeta Config for file
        if self.request.GET.get("zeta_config"):  # User specified config
            zeta_config = Zeta_Config.objects.get(pk=int(self.request.GET["zeta_config"]))
        else:
            zeta_config = zfile.zeta_config if zfile else Zeta_Config.objects.get(pk=ZETA_ZZT32R)

        zeta_config.user_configure(self.request.GET) #  Update config with user requested options
        return zeta_config


def play_zzt_online(request):
    context = {}
    context["title"] = "Play ZZT Online"
    context["components"] = {"controls": True, "instructions": False, "credits": True, "advanced": False, "players": False}
    context["header_text"] = "Play ZZT Online"
    context["local"] = False
    # Worlds to include
    world_pack_key = request.GET.get("world_pack", "official-worlds")
    world_packs = {
        "official-worlds": [1015, 106, 107, 1592, 1593, 1594, 1595, 703, 2145,],
    }
    launch_worlds = {
        "official-worlds": "TOWN",
    }
    context["world_pack_key" ] = world_pack_key
    context["file_ids"] = world_packs.get(world_pack_key)
    context["file_count"] = len(context["file_ids"])
    context["included_files"] = []
    qs = ZFile.objects.filter(pk__in=context["file_ids"]).order_by("release_date")
    for f in qs:
        context["included_files"].append(f.download_url())
    context["file"] = qs.filter(pk=context["file_ids"][0]).first()  # "Prime" zfile
    context["mode"] = request.GET.get("mode", "full")
    context["base"] = "museum_site/play-popout.html" if context["mode"] == "popout" else "museum_site/main.html"
    context["executable"] = "AUTO"
    context["player"] = "zeta"
    context["engine"] = context["executable"]
    context["ZETA_EXECUTABLES"] = ZETA_EXECUTABLES
    context["zeta_config"] = Zeta_Config.objects.get(pk=1)  # TODO Magic Number: ZZT v3.2
    context["zeta_config"].arguments = launch_worlds.get(world_pack_key)
    context["zeta_config"].executable = "zzt32kc-moz.zip"
    context["zeta_database"] = "generic-play-zzt-online-{}".format(world_pack_key)
    context["hide_advanced_settings"] = True
    context["hide_managed_saved_data"] = True
    context["hide_current_zeta_config"] = True
    context["zeta_player_scale"] = int(request.COOKIES.get("zeta_player_scale", 1))

    # Other includes
    context["beginner_friendly_worlds"] = Collection.objects.filter(slug="beginner-friendly-worlds").first()
    context["best1"] = Article.objects.filter(pk=295).first()
    context["best2"] = Article.objects.filter(pk=563).first()

    context["meta_tags"] = Meta_Tag_Block(url=request.get_full_path(), title=context["title"], image="pages/play-zzt-online.png", description="Play ZZT in your browser! Includes the original ZZT saga, The Best of ZZT, and ZZT's Revenge ready to play, along with links to other recommended worlds.")
    return render(request, "museum_site/play-zzt-online.html", context)


@rusty_key_check
def zeta_launcher(request, key=None, components=["controls", "instructions", "credits", "advanced", "players"]):
    data = {"title": "Zeta Launcher", "DETAIL_ANTIQUATED": DETAIL_ANTIQUATED}
    data["components"] = {"controls": False, "instructions": False, "credits": False, "advanced": False, "players": False}
    PLAY_METHODS = {"archive": {"name": "Archive.org - DosBox Embed"}, "zeta": {"name": "Zeta"}}

    # Template rendering mode
    # full - Extends "world.html", has a file header
    # popout - Extends "play-popout.html", removes all site components
    data["mode"] = request.GET.get("mode", "full")

    if data["mode"] == "popout":
        data["base"] = "museum_site/play-popout.html"
        player = "zeta"
    else:
        data["base"] = "museum_site/main.html"
        # Determine visible components
        possible_components = ["controls", "instructions", "credits", "advanced", "players"]
        for possible_component in possible_components:
            data["components"][possible_component] = (possible_component in components)
        # Show advanced settings if requested in URL
        if request.GET.get("advanced"):
            data["components"]["advanced"] = True
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
            if data["file"] and data["file"].supports_zeta_player:
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
    can_change_screenshot = False
    if data["file_count"] == 1 and data["file"].is_detail(DETAIL_UPLOADED) and request.user.is_authenticated:
        if data["file"].upload.user and data["file"].upload.user.pk == request.user.pk:
            data["your_upload"] = True
            can_change_screenshot = True

    if data["file_count"] == 1 and request.user.is_staff:
        can_change_screenshot = True

    if request.method == "POST" and can_change_screenshot:
        image = open_base64_image(request.POST.get("b64img"))
        image = image.crop(IMAGE_CROP_PRESETS["ZZT"])
        image_path = os.path.join(STATIC_PATH, "screenshots/{}/{}.png".format(data["file"].bucket(), data["file"].key))
        image.save(image_path)
        data["file"].has_preview_image = True
        data["file"].save()
        data["screenshot_updated"] = True

    data["meta_tags"] = Meta_Tag_Block(url=request.get_full_path(), title=data["title"], image=data["file"].preview_url(), description="Play {} in your web browser.".format(data["file"].title))
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

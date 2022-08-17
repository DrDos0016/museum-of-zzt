import json
import os
import random
import uuid
import zipfile

from datetime import datetime
from urllib.parse import quote

import requests
from django.db import models
from django.db.models import Q
from twitter import *
from PIL import Image

from museum.settings import STATIC_URL
from museum_site.models.base import BaseModel

from museum_site.common import TEMP_PATH, record
from museum_site.constants import SITE_ROOT
from museum_site.core.detail_identifiers import *
from museum_site.models import File
try:
    from museum_site.private import (
        TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_OAUTH_SECRET,
        TWITTER_OAUTH_TOKEN, WEBHOOK_URL
    )
except ModuleNotFoundError:
    print("PRIVATE.PY NOT FOUND. WOZZT QUEUE CANNOT TWEET OR HOOK TO DISCORD")
import zookeeper


class WoZZT_Queue(BaseModel):
    """ Object representing an upcoming Worlds of ZZT Twitter bot post """
    model_name = "WoZZT-Queue"
    table_fields = ["Date", "Time", "Tweet", "Link"]

    file = models.ForeignKey("File", on_delete=models.SET_NULL, null=True)
    zzt_file = models.CharField(max_length=80)
    board = models.IntegerField()
    board_name = models.CharField(max_length=50, default="")
    dark = models.BooleanField(default=False)
    zap = models.BooleanField(default=False)
    shot_limit = models.IntegerField(default=255)
    time_limit = models.IntegerField(default=0)
    uuid = models.CharField(max_length=36)
    priority = models.IntegerField(
        default=10,
        help_text="Higher priority is used first"
    )
    category = models.CharField(max_length=32, default="wozzt")

    class Meta:
        ordering = ["id"]

    def __str__(self):
        output = "WoZZT Queue {}".format(self.id)
        return output

    def image_path(self):
        output = os.path.join(
            SITE_ROOT, "museum_site", "static", "wozzt-queue",
            self.uuid + ".png"
        )
        return output

    def url(self):
        return "X"

    def preview_url(self):
        return os.path.join(STATIC_URL, "wozzt-queue", self.uuid + ".png")

    def roll(self, category="wozzt", title_screen=False):
        self.uuid = str(uuid.uuid4())
        self.category = category

        qs = File.objects.wozzt().order_by("?")

        # Find first non-banned file
        for f in qs:
            if f.id not in BANNED_FILES:
                self.file_id = f.id
                break

        # Select a random ZZT file in the zip
        zf = zipfile.ZipFile(f.phys_path())
        files = zf.namelist()
        files.sort()

        world_choices = []
        for f in files:
            filename = f.lower()
            if filename.endswith(".zzt") and ("__MACOSX" not in filename):
                world_choices.append(f)

        if not world_choices:
            record("WOZZT_QUEUE.PY: World choices was empty for", self.file_id)
            return False

        selected = random.choice(world_choices)
        self.zzt_file = selected

        # Extract it
        try:
            zf.extract(selected, TEMP_PATH)
        except NotImplementedError:
            record(
                "WOZZT_QUEUE.PY: Failed to extract using file #", self.file_id
            )
            return False

        # Parse the world with Zookeeper
        z = zookeeper.Zookeeper(os.path.join(TEMP_PATH, selected))

        # Select a random board (unless it's meant for Tuesday)
        if title_screen:
            board_possibilities = [0]
        else:
            board_possibilities = list(range(0, len(z.boards)))

        # Remove banned boards from list of possibilities
        banned_boards_key = str(self.file_id) + ":" + self.zzt_file
        if BANNED_BOARDS.get(banned_boards_key):
            banlist = BANNED_BOARDS[banned_boards_key]
            for idx in banlist[::-1]:
                board_possibilities.pop(idx)

        # Remove banned board titles from list of possibilities
        for idx in board_possibilities:
            if z.boards[idx].title in BANNED_BOARD_TITLES:
                try:
                    board_possibilities.remove(idx)
                except ValueError:
                    None  # Already removed earlier

        if len(board_possibilities) == 0:
            record(
                "WOZZT_QUEUE.PY: Ran out of board possibilities #",
                self.file_id
            )
            return False

        board_num = random.choice(board_possibilities)

        z.boards[board_num].screenshot(
            os.path.join(
                SITE_ROOT, "museum_site", "static", "wozzt-queue", self.uuid
            ),
            title_screen=(board_num == 0)
        )
        self.board = board_num
        self.board_name = z.boards[board_num].title

        # Board properties
        # Dark
        if z.boards[board_num].is_dark:
            self.dark = True
        # Zap
        if z.boards[board_num].zap:
            self.zap = True
        # Can fire
        self.shot_limit = z.boards[board_num].can_fire

        # Time limit
        self.time_limit = z.boards[board_num].time_limit

        self.save()
        return True

    def tweet_text(self):
        escaped_file_url = quote("file/" + self.file.letter + "/" + self.file.key + "/")
        escaped_zzt_url = quote(self.zzt_file)

        output = (f"https://museumofzzt.com/{escaped_file_url}?file="
                  f"{escaped_zzt_url}&board={self.board}\n")
        output += f"{self.file.title} by {self.file.author}"
        if self.file.release_date:
            output += " (" + str(self.file.release_date)[:4] + ")\n"
        else:
            output += "\n"
        if self.file.ssv_company:
            output += "Published by: " + str(self.file.ssv_company) + "\n"

        board_properties = []

        # Dark
        if self.dark:
            board_properties.append("🔦")
        # Zap
        if self.zap:
            board_properties.append("⚡")
        # Can fire
        if self.shot_limit != 255:
            board_properties.append(str(self.shot_limit) + " 🔫")
        # Time limit
        if self.time_limit != 0:
            board_properties.append(str(self.time_limit) + " ⏳")

        bp = ""
        if board_properties:
            bp = " {"
            for p in board_properties:
                bp += p + ", "
            bp = bp[:-2] + "}"

        output += f"[{self.zzt_file}] - \"{self.board_name}\"{bp}\n"

        if self.file.supports_zeta_player:
            escaped_play_url = quote(self.file.play_url())
            output += f"https://museumofzzt.com{escaped_play_url}"

        return output

    def tweet_text_short(self):
        escaped_file_url = quote("file/" + self.file.letter + "/" + self.file.key + "/")
        escaped_zzt_url = quote(self.zzt_file)

        output = (f"https://museumofzzt.com/{escaped_file_url}?file="
                  f"{escaped_zzt_url}&board={self.board}\n")
        output += f"{self.file.title} [...]"

        return output

    def send_tweet(self, tweet_related=True, discord_hook=True):
        try_shorter = False  # Try a shorter variant if this one is too long
        # Tweet the image
        with open(self.image_path(), "rb") as imagefile:
            imagedata = imagefile.read()

            t_up = Twitter(
                domain='upload.twitter.com',
                auth=OAuth(
                    TWITTER_OAUTH_TOKEN, TWITTER_OAUTH_SECRET,
                    TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET
                )
            )
            img1 = t_up.media.upload(media=imagedata)["media_id_string"]
            t = Twitter(auth=OAuth(
                TWITTER_OAUTH_TOKEN, TWITTER_OAUTH_SECRET,
                TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET
            ))

            try:
                resp = t.statuses.update(
                    status=self.tweet_text(), media_ids=img1, tweet_mode="extended"
                )
            except TwitterHTTPError as error:
                for err in error.response_data.get("errors", []):
                    if err.get("code") == 186:  # "Tweets needs to be a bit shorter.":
                        try_shorter = True

                if not try_shorter:
                    return False

            if try_shorter:
                try:
                    resp = t.statuses.update(
                        status=self.tweet_text_short(), media_ids=img1, tweet_mode="extended"
                    )
                except TwitterHTTPError as error:
                    self.category = "failed"
                    self.save()
                    return False

            #record(resp)
            twitter_id = resp.get("id")
            twitter_img = resp["entities"]["media"][0]["media_url"]

        # Twitter - Related Articles
        if tweet_related and twitter_id:
            related_count = self.file.articles.filter(
                published=True
            ).exclude(category="Publication Pack").count()

            if related_count:
                article_text = (
                    f"More information on \"{self.file.title}\" is available "
                    f"here: https://museumofzzt.com{self.file.article_url()}"
                )
                resp = t.statuses.update(
                    status=article_text, in_reply_to_status_id=twitter_id
                )

        if discord_hook and twitter_id:
            """ This is duplicate code and should be a function """
            board_properties = []

            # Dark
            if self.dark:
                board_properties.append("🔦")
            # Zap
            if self.zap:
                board_properties.append("⚡")
            # Can fire
            if self.shot_limit != 255:
                board_properties.append(str(self.shot_limit) + " 🔫")
            # Time limit
            if self.time_limit != 0:
                board_properties.append(str(self.time_limit) + " ⏳")

            bp = ""
            if board_properties:
                bp = " {"
                for p in board_properties:
                    bp += p + ", "
                bp = bp[:-2] + "}"

            discord_post = (
                "https://twitter.com/worldsofzzt/status/{}\n**{}** by {} ({})"
                "\n"
            )
            if self.file.ssv_company:
                discord_post += "Published by: {}\n".format(self.file.ssv_company)
            discord_post += "`[{}] - \"{}\"` {}\n"
            discord_post += (
                "Explore: https://museumofzzt.com" +
                quote(self.file.view_url()) + "?file=" + quote(self.zzt_file) +
                "&board=" + str(self.board) + "\n"
            )
            if self.file.archive_name:
                discord_post += (
                    "Play: https://museumofzzt.com" +
                    quote(self.file.play_url())
                )

            discord_post = discord_post.format(
                twitter_id, self.file.title, self.file.author,
                str(self.file.release_date)[:4], quote(self.zzt_file),
                self.board_name, bp
            )

            discord_data = {
                "content": discord_post,
                "embeds": [
                    {"image": {"url": twitter_img}}
                ]
            }
            resp = requests.post(
                WEBHOOK_URL, headers={"Content-Type": "application/json"},
                data=json.dumps(discord_data)
            )
            record(resp)
            record(resp.content)
        return True

    def delete_image(self):
        try:
            os.remove(self.image_path())
        except FileNotFoundError:
            None
        return True

    def detailed_block_context(self, *args, **kwargs):
        debug = True
        context = dict(
            pk=self.pk,
            model=self.model_name,
            preview=dict(url=self.preview_url, alt=self.preview_url),
            url=self.url,
            columns=[],
            title={"datum": "title", "value":"-----"},
        )

        context["columns"].append([
            {"datum": "text-area", "label":"Tweet", "name": "wozzt-tweet", "value":self.tweet_text(), "readonly":True},
            {"datum": "link", "label":"Source", "value":"View", "url":self.file.url() + "?file={}&board={}".format(
                    self.zzt_file, self.board
                ), "target": "_blank" }
        ])

        if debug:
            context["columns"][0].append({"datum": "link", "label":"ID", "value":self.id, "target":"_blank", "kind":"debug", "url":self.admin_url()})
            context["columns"][0].append({"datum": "custom-wozzt-priority", "pk":self.id, "priority":self.priority, "kind":"debug"})
            context["columns"][0].append({"datum": "custom-wozzt-delete", "pk":self.id, "kind":"debug"})
        else:
            context["columns"][0].append(
                {"datum": "text", "label":"Priority", "value":self.priority}
            )
        return context


# Files banned from Worlds of ZZT Bot's feed
BANNED_FILES = [
    951,  # G**g J*****n And STK Revealed
    1779,  # 1**9 T*o
    1577,  # 9**1: A Z*T M******l
    1927,  # N**e E*****n
    1811,  # B*N L***N!!
    1947,  # B*****e (1 in 5 chance of r-slur)
    1852,  # M*****a R***s
    2064,  # M*****a R***s SE
    1496,  # B******! (Author's request)
    2542,  # E**e K****e M****m-M***k! (Author's request)
    1539,  # F*x F***e F**e (Racial caricatures, edgy sexual opinions)
    493,  # G***D P**t 1! (Author's request)
    494,  # G***D P**t 2! (Author's request)
    2246,  # G***D S********k! (Author's request)
    2242,  # M*****'s Z*T T*******s (Author's request)
    2236,  # M**n G****e (Sexual content)
    739,  # M***y A*d T*e Q***t F*r L***! (Sexual content between early teens)
    853,  # P******l (Author's request)
    1197,  # P******l B* (Author's request)
    1660,  # R*****e (Author's request)
    1922,  # R**a P***s (Racial stereotypes)
    925,  # T*e P****e F***s I* (Author's request)
    1723,  # T***h (Author's request)
    2059,  # M****m B***s A*******y (Harassing)
    2095,  # M****m B***s 3 (Harassing)
    2540,  # M****m B***s 4 (Harassing)
    2087,  # M****m B***s 1 (Harassing)
    2084,  # M****m B***s 2 (Harassing)
    1823,  # P******e P****e (Nudity)
    1077,  # S**n (Plenty of N-bombs)
    1933,  # S (Some impressively detailed nudity)
    2010,  # S*****u (Racial caricatures)
    966,  # L*s R******s 1 (Harassing)
    688,  # L*s R******s 6 (Harassing)
    2824,  # L*s R******s 7 (Harassing)
    2825,  # L*s R******s 8 (Harassing)
    689,  # L*s R******s 9 (Harassing),
    130,  # O*******n B******o (Nudity),
]


BANNED_BOARDS = {
    # Format: {File ID:ZZT Filename}: (Board #, Board #, ...)
    "1801:zztv8-1.zzt": (0, 1, 2),
    "1801:zztv8-2.zzt": (
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19
    ),
    "1801:zztv8-3.zzt": (0, 1, 2, 12, 13, 14, 15, 16, 17),
    "1801:zztv8-4.zzt": (0, 1, 2, 12, 13, 14, 15, 16, 17),
    "1901:zztv9-1.zzt": (0, 1, 2, 51),
    "1901:zztv9-2.zzt": (0, 1, 2),
    "1901:zztv9-3.zzt": (0, 1, 2),
    "1901:zztv9-4.zzt": (0, 1, 2),
    "1901:zztv9-5.zzt": (
        0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
        21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32
    ),
}


BANNED_BOARD_TITLES = [
    "!;MadTom's ColorKit", "!;MadTom's ZZToolKit", "!The NOC Color Kit",
    "$ **.**Tripping Color Kit**.**", "$- == (( ( paramach ) )) == -",
    "$ K Z T - Color Kit", "$ ZZT Palette Plus v1.1", "$-( Blend Box )-",
    "$(( ( Paranoid Machinations ) ))", "$() Dude Scott This is Josh ()",
    "$({[/-=+Colors R' Us 2.25 +=-\\]})", "$(= SGP ColorKit v1.0 =)",
    "$)][( dexter's pepsi-kit )][(", "$*)|(* dexscam! *)|(*",
    "$*-*-* Mega Color Box '98 *-*-*", "$**GameMstr1's MegaShades Board**",
    "$*-< CorPuS HeRmetIcUm >-*", "$*-=yllek's kewl color board=-*",
    "$:: hm's wonkeriffic toolkit ::", "$::<< BenKit >>::", "$:[ dexkit ]:",
    "$:{*pisces~iscariot*}  version 666", "$:-BesTK-:",
    "$[[[ [  suburbiaTRiUMPHANT  ] ]]]", "$[] DarkMage ColorKit []",
    "$[=- textures by eJECTION13 -=]", "$[glt-kit by tboT]",
    "$[Jacob Hammond's Colorkit]", "$_/\" VisuoFunctional Spectrum _/\"",
    "$_Underscore_", "$+*=-{[ULTIMA COLOR BOARD]}-=*+",
    "$-+=Flame, Inc. Color Kit=+-", "$-+-The-Shaft-tool-kit-+-",
    "$<(divided)>",
    "$<> FutureWare Blending Kit <>", "$-= Raichu's Circuitbox v6.28 =-",
    "$-=([ <3\\/|$|0/\\/ ])=-", "$-=(MRFLOYDS COLOR BOX)=-",
    "$-=* * * 3 Palette * * *=-", "$-=\\EM's Damn ZZT-Kit/=-",
    "$-=|DirrCo Krazie Kitt 3|=-", "$-=+*PARASITE'S TOOL KIT*+=-",
    "$--==::Noboyuki's ToolSet::==--", "$--==<<BenKit 2 (or BQKiT)>>==--",
    "$==--Magical Mystical ColorBox--==", "$-=Mondo SaxxonPike ToolBox=-",
    "$-=SNACK 4.0 (board 1)=-", "$-=SNACK 4.0 (Board 2)=-",
    "$>>COLOR TOOLBOX<<", "$3d vFINAL - Josh Microwave",
    "$A.I.Z.I Advanced with ZOP", "$AKWare Tool-Kit", "$AKWare Tool-Kit V2.0",
    "$ALL v1.0 for ZZT", "$barrel 'o fun kit", "$Bocco11's ZZToolkit v1.10",
    "$Creemy Chock n' Cheez Froot Lumps", "$DGE Color Kit",
    "$DrCrab's Crammed Board", "$Dude Scott This is Josh V3.0",
    "$Ed's Colorkit", "$Embassy Games Color Center",
    "$Headache- Inducing- Evil.", "$HGSI Coloring Kit (v4)",
    "$JM's All Purpose ZZT Toolbox", "$KPCK V. 1.0", "$MIG toolkit",
    "$Misteroo Rebellion/AKWare Toolkit", "$MNMZ Soft Toolkit v1.3",
    "$Mystical Winds TK - Art Set Adv.", "$Mystickcal Color Toolkit",
    "$Newt's Toolbox", "$packboard.v1.aetsch.if.2000",
    "$Ra/\\/|)()/\\/\\ I/\\/C TK V. NUTS", "$ROOKIT 2", "$Shades Toolbox",
    "$SIMBA SEZ ROAR", "$Spectracolor", "$StreamLineSTK versionArr",
    "$Terrain Toolbox - Ice", "$The KjKit!   Board 3", "$The KjKit!  Board 2",
    "$The KjKit! Board 1", "$The KjKit! Board 2", "$The KjKit! Board 3",
    "$The ZZT First Aid Kit", "$Ultra Colour", "$Vecchio's Toolkit",
    "$vin3y $hades Toolbo><", "$VINEY80X", "$vstk - v. peter gabriel", "$wtog",
    "$ZZT First Aid Kit", "$ZZTek Color Board - by kev carter",
    "$ZZTek Colour Kit", "::   - ZZT Rainbow v3.7 -   ::",
    ":: NMZmaster Toolkit v3.0", "::/\\/omo(7) update!",
    "::z.nadir's palace of bullet::", ":; 2z + t", ":; Compressed Textkit",
    ":; Friday Night Fever", ":; UseLESSS ReDUNDAncYYYYy",
    ":;.silverspectrum v.karma", ":;[ the draco toolkit ]",
    ":;_-=(EarthquakeTK)=-_", ":;_-=+X(ETK 2)X+=-_",
    ":;-=( beef's ultra funky tool kit", ":;-=*Raptorian's Toolbox v2.1*=-",
    ":;Dave's ARG! PG Tool-kit", ":;dexmono vthe fly",
    ":;lemmer toolkit: v100", ":;lemmer's ascii chart on fire",
    ":;Quantum's Toolkit (1)", ":;Quantum's Toolkit (3)",
    ":;rom v. hall of heads2k", ":WinS Toolbox v2.5", "Quantum's Toolkit (2)",
    "Quantum's Toolkit (4)", "*NEW STK--Objects",
    "*NEW STK--Objects, Blinking", "*NEW STK--Boulders, Both",
    "*NEW STK--N/S Sliders, Both", "*NEW STK--E/W Sliders, Both",
    "*NEW STK--Gems, Both", "*NEW STK--Keys, Both",
    "*NEW STK--Normal Walls, Both", "*NEW STK--Breakable Walls, Both",
    "*NEW STK--Invisible Walls, Both", "*NEW STK--Fake Walls, Both",
    "*NEW STK--Water, Both", "*NEW STK--Bombs", "*NEW STK--Bombs, Blinking",
    "*NEW STK--Pushers", "*NEW STK--Pushers, Blinking",
    "*NEW STK--Spinning Guns", "*NEW STK--Spinning Guns, Blinking",
    "*NEW STK--CounterClockwise", "*NEW STK--CounterCl., Blinking",
    "*NEW STK--Clockwise", "*NEW STK--Clockwise, Blinking",
    "*NEW STK--Transporters", "*NEW STK--Transporters, Blinking",
    "*NEW STK--Blink Walls", "*NEW STK--Blink Walls, Blinking",
    "*NEW STK--Centipede Heads", "*NEW STK--Centip. Heads, Blinking",
    "*NEW STK--Line Walls, Both", "*NEW STK--Solid Walls, Both",
    "*NEW STK--Pre Activated Bombs", "*NEW STK--Bullets",
    "*NEW STK--Ammo, Torches, more", "*NEW STK--Doors, Passages, Floors",
    "*NEW STK--Ricochet", "*NEW STK--Strange Stuff",
    "*NEW STK--More Strange Stuff", "*MORESTK--Ammo, Both",
    "*MORESTK--Torches, Both", "*MORESTK--Doors, Both",
    "*MORESTK--Star, Bl enemies, etc.", "*MORESTK--More Passages",
    "*MORESTK--Duplicators", "*MORESTK--Dupes, Blinking",
    "*MORESTK--In-process Dupes", "*MORESTK--PreActivatedBombs1",
    "*MORESTK--PreActivatedBombs2", "*MORESTK--PreActivatedBombs3",
    "*MORESTK--Energizers, Both", "*MORESTK--Forests, Both",
    "*MORESTK--Horiz. BWall Rays", "*MORESTK--All Bullets",
    "*MORESTK--Ricochets, Both", "*MORESTK--Text: B, G, Cy, R",
    "*MORESTK--Text: P, Y, W", "*MORESTK--Still Bullets, Both",
    "*MORESTK--Empties, Both", "*WEIRDSTK--Crosses", "*WEIRDSTK--Passages",
    "*WEIRDSTK--Carrots", "*WEIRDSTK--Dead pushers", "*WEIRDSTK--Smilies",
    "*WEIRDSTK--Dead bears", "*WEIRDSTK--Dead ruffians",
    "*WEIRDSTK--Dead lions", "*WEIRDSTK--Dead tigers", "*WEIRDSTK--Dead heads",
    "*WEIRDSTK--Dead segments", "*WEIRDSTK--Breakables",
    "*WEIRDSTK--Breakables, blinking", "*WIL STK--MONITORs w/o stats",
    "*WIL STK--Monitors", "*WIL STK--Monitors, Blinking", "*WIL STK--Slimes",
    "*WIL STK--Slimes, Blinking", "*WIL STK--Slimes w/o stats",
    "*WIL STK--Hyper Enemies", "*WIL STK--More Hyper Enemies",
    "*WIL STK--Faster/Slower Bombs", "*WIL STK--Scroll to Fakes",
    "*WIL STK--Scroll to Fakes, Blinkin",
]

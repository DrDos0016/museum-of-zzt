import json
import os
import random
import tempfile
import uuid
import zipfile

from datetime import datetime, UTC
from urllib.parse import quote


import pytumblr
import requests
import tweepy

from django.db import models
from django.template.loader import render_to_string
from mastodon import Mastodon


from museum.settings import STATIC_URL
from museum_site.constants import STATIC_PATH, APP_ROOT
from museum_site.core.misc import record, zookeeper_init
from museum_site.core.social import Social_Bluesky
from museum_site.models import BaseModel, File
from museum_site.querysets.wozzt_queue_querysets import *
from museum_site.settings import (
    TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_OAUTH_SECRET, TWITTER_OAUTH_TOKEN, TWITTER_BEARER_TOKEN,
    WEBHOOK_URL,
    TUMBLR_OAUTH_CONSUMER, TUMBLR_OAUTH_CONSUMER_SECRET, TUMBLR_OAUTH_TOKEN, TUMBLR_OAUTH_SECRET,
    MASTODON_ACCESS_TOKEN, MASTODON_CLIENT_KEY, MASTODON_CLIENT_SECRET, MASTODON_EMAIL, MASTODON_PASS,
    MASTODON_SECRETS_FILE,
)


class WoZZT_Queue(BaseModel):
    """ Object representing an upcoming Worlds of ZZT Twitter bot post """
    objects = WoZZT_Queue_Queryset.as_manager()
    model_name = "WoZZT-Queue"
    table_fields = ["Date", "Time", "Tweet", "Link"]
    media_url = ""  # Used for Discord webhook

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
        output = os.path.join(STATIC_PATH, "wozzt-queue", self.uuid + ".png")
        return output

    def url(self):
        return "X"

    def get_absolute_url(self):
        return "X"

    def preview_url(self):
        return os.path.join("wozzt-queue", self.uuid + ".png")

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
        TEMP_DIR = tempfile.TemporaryDirectory(prefix="moz-")
        TEMP_PATH = TEMP_DIR.name
        try:
            zf.extract(selected, TEMP_PATH)
        except NotImplementedError:
            record("WOZZT_QUEUE.PY: Failed to extract using file #", self.file_id)
            return False

        # Parse the world with Zookeeper
        z = zookeeper_init(os.path.join(TEMP_PATH, selected))

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
            record("WOZZT_QUEUE.PY: Ran out of board possibilities #", self.file_id)
            return False

        board_num = random.choice(board_possibilities)

        z.boards[board_num].screenshot(os.path.join(STATIC_PATH, "wozzt-queue", self.uuid), title_screen=(board_num == 0))
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

    def render_text(self, medium):
        now = datetime.now(UTC)
        context = {
            "board_url": self.file.get_absolute_url() + "?file=" + quote(self.zzt_file) + "&board=" + str(self.board),
            "zfile_title": self.file.title,
            "zfile_author": self.file.related_list("authors"),
            "zfile_year": self.file.release_year(),
            "zfile_company": self.file.related_list("companies"),
            "zfile_world": self.zzt_file,
            "zfile_board": self.board_name,
            "zfile_board_properties": self.get_zfile_board_properties(),
            "play_url": self.file.play_url(),
            "zfile": self.file,
            "related_article_count": self.file.articles.published().exclude(category="Publication Pack").count(),
            "article_url": self.file.article_url(),
        }

        return render_to_string("museum_site/subtemplate/wozzt-{}.html".format(medium), context).strip()

    def get_zfile_board_properties(self):
        output = []
        if self.dark:
            output.append("🔦")
        if self.zap:
            output.append("⚡")
        if self.shot_limit != 255:
            output.append("🔫: " + str(self.shot_limit)),
        if self.time_limit:
            output.append("⏳: " + str(self.time_limit)),
        return output

    def send_tumblr(self):
        tags = self.file.related_list("authors") + [self.file.title] + [self.file.key.lower()]
        if self.category == "tuesday":
            tags.append("title screen tuesday")
        client = pytumblr.TumblrRestClient(TUMBLR_OAUTH_CONSUMER, TUMBLR_OAUTH_CONSUMER_SECRET, TUMBLR_OAUTH_TOKEN, TUMBLR_OAUTH_SECRET)
        resp = client.create_photo("worldsofzzt", state="published", tags=tags, caption=self.render_text("tumblr"), data=self.image_path())
        return resp

    def send_bluesky(self, post_related=True):
        s = Social_Bluesky()
        s.upload_media(self.image_path())
        resp = s.post(body=self.render_text("bluesky"))

        if post_related:
            related_count = self.file.articles.published().exclude(category="Publication Pack").count()
            if related_count:
                article_text = (f"More information on \"{self.file.title}\" is available here: https://museumofzzt.com{self.file.article_url()}")
                s.wozzt_reply(resp, article_text)
        return True

    def send_tweet(self, tweet_related=True):
        try_shorter = False  # Try a shorter variant if this one is too long

        # Connect via Tweepy
        client = tweepy.Client(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_CONSUMER_KEY,
            consumer_secret=TWITTER_CONSUMER_SECRET,
            access_token=TWITTER_OAUTH_TOKEN,
            access_token_secret=TWITTER_OAUTH_SECRET,
        )

        tweepy_v1_auth = tweepy.OAuth1UserHandler(
            TWITTER_CONSUMER_KEY,
            TWITTER_CONSUMER_SECRET,
            TWITTER_OAUTH_TOKEN,
            TWITTER_OAUTH_SECRET,
        )
        tweepy_v1 = tweepy.API(tweepy_v1_auth)

        # Upload image
        media = tweepy_v1.media_upload(self.image_path())
        # Tweet
        resp = client.create_tweet(media_ids=[media.media_id], in_reply_to_tweet_id=None, text=self.render_text("twitter"))
        twitter_id = resp.data.get("id", 0)

        # Twitter - Related Articles
        if tweet_related and twitter_id:
            related_count = self.file.articles.published().exclude(category="Publication Pack").count()

            if related_count:
                article_text = (f"More information on \"{self.file.title}\" is available here: https://museumofzzt.com{self.file.article_url()}")
                resp = client.create_tweet(in_reply_to_tweet_id=twitter_id, text=article_text)
        return True

    def send_mastodon(self):
        # Log in
        mastodon = Mastodon(
            client_id=MASTODON_CLIENT_KEY,
            client_secret=MASTODON_CLIENT_SECRET,
            access_token=MASTODON_ACCESS_TOKEN,
            api_base_url="https://mastodon.social"
        )

        # Upload the image
        media_resp = mastodon.media_post(media_file=self.image_path())
        if media_resp.get("id"):
            self.media_url = media_resp.get("url", "")
            toot_resp = mastodon.status_post(status=self.render_text("mastodon"), media_ids=[media_resp["id"]])
        else:
            return media_resp

        return toot_resp

    def send_discord(self):
        """ Requires an image url to attach. Cron uses Mastodon image. """
        if not self.media_url:
            record("Cannot send to Discord without setting self.media_url")
            return False
        discord_data = {"content": self.render_text("discord"), "embeds": [{"image": {"url": self.media_url}}]}
        resp = requests.post(WEBHOOK_URL, headers={"Content-Type": "application/json"}, data=json.dumps(discord_data))
        record(resp)
        record(resp.content)
        return True

    def delete_image(self):
        try:
            os.remove(self.image_path())
        except FileNotFoundError:
            None
        return True

    def get_field_view(self, view="detailed"):
        return {"value": "--"}

    def get_field_tweet(self, view="detailed"):
        return {"label": "Tweet", "value": "<textarea name='wozzt-tweet' readonly>{}</textarea>".format(self.render_text("twitter")), "safe": True}

    def get_field_source(self, view="detailed"):
        url = self.file.get_absolute_url() + "?file={}&board={}".format(self.zzt_file, self.board)
        return {"label": "Source", "value": "<a href='{}' target='_blank'>View</a>".format(url), "safe": True}

    def get_field_priority(self, view="detailed"):
        return {"label": "Priority", "value": "<input name='priority' value='{}'> <input name='update-priority' type='button' value='Apply'>".format(self.priority), "safe": True}

    def get_field_delete(self, view="detailed"):
        return {"label": "Delete", "value": "<input name='delete' type='button' value='Delete'>", "safe": True}


    def context_detailed(self):
        context = self.context_universal()
        context["roles"] = ["model-block", "detailed"]
        context["columns"] = []

        columns = [
            ["tweet", "source"],
        ]

        if self.show_staff:
            columns[0] += ["priority", "delete"]

        for col in columns:
            column_fields = []
            for field_name in col:
                field_context = self.get_field(field_name)
                column_fields.append(field_context)
            context["columns"].append(column_fields)
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

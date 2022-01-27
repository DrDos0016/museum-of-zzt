import hashlib
import io
import os
import subprocess
import zipfile

from datetime import datetime
from random import randint, seed, shuffle

from django.db import models
from django.db.models import Avg, Q
from django.template.defaultfilters import date, filesizeformat

try:
    import zookeeper
    HAS_ZOOKEEPER = True
except ImportError:
    HAS_ZOOKEEPER = False

from .common import (
    slash_separated_sort, zipinfo_datetime_tuple_to_str, UPLOAD_CAP,
    STATIC_PATH, optimize_image
)
from .constants import SITE_ROOT, ZETA_RESTRICTED, LANGUAGES
from .review import Review
from .article import Article

DETAIL_DOS = 1
DETAIL_WIN16 = 2
DETAIL_WIN32 = 3
DETAIL_WIN64 = 4
DETAIL_LINUX = 5
DETAIL_OSX = 6
DETAIL_FEATURED = 7
DETAIL_CONTEST = 8
DETAIL_ZZM = 9
DETAIL_GFX = 10
DETAIL_MOD = 11
DETAIL_ETC = 12
DETAIL_SZZT = 13
DETAIL_UTILITY = 14
DETAIL_ZZT = 15
DETAIL_ZIG = 16
DETAIL_LOST = 17
DETAIL_UPLOADED = 18
DETAIL_REMOVED = 19
DETAIL_CORRUPT = 20


class FileManager(models.Manager):
    def basic_search(self, q):
        return self.filter(
            Q(title__icontains=q) |
            Q(aliases__alias__icontains=q) |
            Q(author__icontains=q) |
            Q(filename__icontains=q) |
            Q(company__icontains=q)
        ).distinct()

    def directory(self, category):
        if category == "company":
            return self.values(
                "company"
            ).exclude(
                company=None
            ).exclude(
                company=""
            ).distinct().order_by("company")
        elif category == "author":
            return self.values("author").distinct().order_by("author")

    def identifier(self, identifier=None, letter=None, filename=None):
        if identifier is None:
            return self.filter(letter=letter, filename=filename)

    def latest_additions(self):
        return self.filter(
            spotlight=True
        ).exclude(
            Q(details__id__in=[DETAIL_UPLOADED]) |
            Q(release_date__gte="2021-01-01")
        ).order_by("-publish_date", "-id")

    def new_releases(self):
        return self.filter(
            spotlight=True, release_date__gte="2021-01-01"
        ).exclude(
            details__id__in=[DETAIL_UPLOADED]
        ).order_by("-publish_date", "-id")

    def published(self):
        return self.exclude(details__id__in=[DETAIL_UPLOADED, DETAIL_LOST])

    def search(self, p):
        qs = File.objects.all()
        return qs

    def standard_worlds(self):
        return self.filter(
            details__id__in=[DETAIL_ZZT, DETAIL_SZZT, DETAIL_UPLOADED]
        )

    def random_zzt_world(self):
        excluded_details = [
            DETAIL_LOST, DETAIL_REMOVED, DETAIL_UPLOADED, DETAIL_CORRUPT
        ]
        max_pk = self.all().order_by("-id")[0].id

        zgame = None
        while not zgame:
            pk = randint(1, max_pk)
            zgame = self.filter(pk=pk, details__id=DETAIL_ZZT).exclude(
                details__id__in=excluded_details
            ).exclude(genre__icontains="Explicit").first()

        return zgame

    def roulette(self, rng_seed, limit):
        details = [DETAIL_ZZT, DETAIL_SZZT, DETAIL_UTILITY]

        # Get all valid file IDs
        ids = list(
            self.filter(details__id__in=details).values_list("id", flat=True)
        )

        # Shuffle them
        seed(rng_seed)
        shuffle(ids)

        # Return them in a random order
        return File.objects.filter(id__in=ids[:limit]).order_by("?")

    def unpublished(self):
        return self.filter(details__id__in=[DETAIL_UPLOADED])

    def wozzt(self):
        excluded_details = [
            DETAIL_UPLOADED, DETAIL_GFX, DETAIL_LOST, DETAIL_CORRUPT
        ]
        return self.filter(
            details__in=[DETAIL_ZZT]
        ).exclude(
            Q(details__in=excluded_details) |
            Q(author__icontains="_ry0suke_") |
            Q(genre__icontains="explicit")
        )

    def featured_worlds(self):
        return self.filter(details=DETAIL_FEATURED)

    """ TODO: Move this to something more generic than File objects """
    def reach(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None



class File(models.Model):
    """ File object repesenting an upload to the site """

    objects = FileManager()

    ## Newfunc
    SPECIAL_SCREENSHOTS = ["zzm_screenshot.png"]
    ## Endnewfunc

    """
    Fields:
    letter          -- Letter the file can be found under via browse pages
    filename        -- Name of the (Zip) file (ex: Respite.zip)
    title           -- Name of the World (ex: Frost 1: Power)
    sort_title      -- Title used for natural sorting
    author          -- / sep. ABC list of authors (ex: Hercules/Nadir)
    size            -- Filesize in bytes (ex: 420690)
    genre           -- / sep. ABC list of genres (ex: Action/RPG)
    release_date    -- Best guess release date (ex: 2001-04-16)
    release_source  -- Source of release date (ex: ZZT file, News post, Text)
    screenshot      -- Filename of screenshot to display (ex: 3dtalk.png)
    company         -- / sep. ABC list of companies published (ex: ERI/IF)
    description     -- Description of file for utilities or featured games
    review_count    -- Number of reviews on this file
    rating          -- Average rating if any, from file's reviews
    details         -- Link to Detail objects
    articles        -- Link to Article objects
    article_count   -- Number of articles associated with this file
    checksum        -- md5 checksum of the zip file
    superceded      -- FK with File for the "definitive" version of a file
    playable_boards -- Number of boards in file that can be accessed in play
    total_boards    -- Number of boards in file that exist period
    archive_name    -- name on archive.org (ex: zzt_burgerj)
    aliases         -- Link to Alias objects
    spotlight       -- Allow appearance on front page
    can_review      -- Allow reviews on the file
    license         -- File license if available
    license_source  -- Source of license information
                       (ex: LICENSE file, documentation, game.zzt)
    downloads       -- Reference to Download sources
    language        -- / sep. ABC list of language codes (ISO 639-1)
    explicit        -- If the file contains explicit content
    """

    letter = models.CharField(max_length=1, db_index=True, editable=False)
    filename = models.CharField(max_length=50)
    size = models.IntegerField(default=0, editable=False)
    title = models.CharField(max_length=80)
    author = models.CharField(max_length=255)
    company = models.CharField(
        max_length=255, default="", blank=True,
    )
    genre = models.CharField(max_length=255)
    release_date = models.DateField(default=None, null=True, blank=True)
    release_source = models.CharField(
        max_length=20, null=True, default=None, blank=True
    )
    language = models.CharField(max_length=50, default="en")
    description = models.TextField(null=True, blank=True, default="")
    playable_boards = models.IntegerField(
        null=True, blank=True, default=None,
        help_text="Set automatically. Do not adjust."
    )
    total_boards = models.IntegerField(
        null=True, blank=True, default=None,
        help_text="Set automatically. Do not adjust."
    )
    archive_name = models.CharField(
        max_length=80,
        default="",
        blank=True,
        help_text="ex: zzt_burgerj"
    )

    screenshot = models.CharField(
        max_length=80, blank=True, null=True, default=None
    )

    license = models.CharField(max_length=150, default="Unknown")
    license_source = models.CharField(max_length=150, default="", blank=True)

    # Derived Data
    checksum = models.CharField(
        max_length=32, null=True, blank=True, default=""
    )
    sort_title = models.CharField(
        max_length=100, db_index=True, default="", blank=True,
        help_text="Leave blank to set automatically"
    )

    # Reviews
    review_count = models.IntegerField(
        default=0, help_text="Set automatically. Do not adjust."
    )
    rating = models.FloatField(null=True, default=None, blank=True)

    # Museum Properties
    explicit = models.BooleanField(default=False)
    spotlight = models.BooleanField(default=True)
    can_review = models.BooleanField(default=True)
    publish_date = models.DateTimeField(
        null=True, default=None, db_index=True, blank=True,
        help_text="Date File was published on the Museum"
    )
    last_modified = models.DateTimeField(
        auto_now=True,
        help_text="Date DB entry was last modified"
    )

    # Associations
    aliases = models.ManyToManyField("Alias", default=None, blank=True)
    articles = models.ManyToManyField(
        "Article", default=None, blank=True
    )
    article_count = models.IntegerField(
        default=0, editable=False
    )
    details = models.ManyToManyField("Detail", default=None, blank=True)
    downloads = models.ManyToManyField("Download", default=None, blank=True)
    zeta_config = models.ForeignKey(
        "Zeta_Config", null=True, blank=True, default=1,
        on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ["sort_title", "letter"]

    def __str__(self):
        return "[" + str(self.id) + "] " + self.title

    def basic_save(self, *args, **kwargs):
        super(File, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Pre save
        # Force lowercase letter
        if not self.letter:
            self.letter = self.letter_from_title()
        else:
            self.letter = self.letter.lower()

        # Sort genres
        self.genre = slash_separated_sort(self.genre)

        # Create sorted title
        self.calculate_sort_title()

        # Recalculate Article Count
        self.calculate_article_count()

        # If the screenshot is blank and a file exists for it, set it
        file_exists = os.path.isfile(
            os.path.join(SITE_ROOT, "museum_site/static/images/screenshots/") +
            self.letter + "/" + self.filename[:-4] + ".png"
        )
        if self.screenshot == "" and file_exists:
            self.screenshot = self.filename[:-4] + ".png"

        # Calculate Review Scores
        self.calculate_reviews()

        # Update blank md5s
        if self.checksum == "" or self.checksum is None:
            self.calculate_checksum()

        # Set board counts for non-uploads
        if HAS_ZOOKEEPER and not kwargs.get("new_upload"):
            if not self.playable_boards or not self.total_boards:
                self.calculate_boards()

        # Actual save call
        if kwargs.get("new_upload"):
            del kwargs["new_upload"]
        super(File, self).save(*args, **kwargs)

    def jsoned(self):
        data = {
            "letter": self.letter,
            "filename": self.filename,
            "title": self.title,
            "sort_title": self.sort_title,
            "author": self.author,
            "size": self.size,
            "genres": self.genre_list(),
            "release_date": self.release_date,
            "release_source": self.release_source,
            "screenshot": self.screenshot,
            "company": self.company,
            "description": self.description,
            "review_count": self.review_count,
            "rating": self.rating,
            "details": [],
            "articles": [],
            "aliases": [],
            "article_count": self.article_count,
            "checksum": self.checksum,
            "playable_boards": self.playable_boards,
            "total_boards": self.total_boards,
            "archive_name": self.archive_name,
            "publish_date": self.publish_date,
            "last_modified": self.last_modified,
        }

        for d in self.details.all():
            data["details"].append({"id": d.id, "detail": d.detail})

        for a in self.articles.all().only("id", "title"):
            data["articles"].append({"id": a.id, "title": a.title})

        for a in self.aliases.all():
            data["aliases"].append({"id": a.id, "alias": a.alias})

        return data

    def calculate_sort_title(self):
        # Handle titles that start with A/An/The
        sort_title = self.title.lower()

        if sort_title.startswith(("a ", "an ", "the ")):
            sort_title = sort_title[sort_title.find(" ") + 1:]

        # Expand numbers
        words = sort_title.split(" ")
        expanded = []
        for word in words:
            try:
                int(word)
                expanded.append(("0000" + word)[-4:])
            except ValueError:
                expanded.append(word)
        sort_title = " ".join(expanded)

        self.sort_title = sort_title
        return True

    def letter_from_title(self):
        """ Returns the letter a file should be listed under after removing
        articles """
        title = self.title.lower()
        if title.startswith("the "):
            title = title.replace("the ", "", 1)
        elif title.startswith("a "):
            title = title.replace("a ", "", 1)
        if title.startswith("an "):
            title = title.replace("an ", "", 1)

        letter = title[0]
        if letter not in "abcdefghijklmnopqrstuvwxyz":
            letter = "1"
        return letter

    def download_url(self):
        if (not self.id) or self.is_uploaded():
            return "/zgames/uploaded/" + self.filename
        else:
            return "/zgames/" + self.letter + "/" + self.filename

    def download_anchor(self, text="Download"):
        url = self.download_url()
        ellipses = ""

        if self.downloads.count():
            url = "/download/{}/{}".format(self.letter, self.filename)
            ellipses = "s…"

        html = ('<a href="{url}" class="download-link{explicit_class}">'
                '{text}{ellipses}</a>').format(
            url=url,
            text=text,
            explicit_class=(" explicit" if self.explicit else ""),
            ellipses=ellipses
        )
        return html

    def download_anchor_small(self):
        return self.download_anchor(text="DL")

    def file_exists(self):
        return True if os.path.isfile(self.phys_path()) else False

    def play_url(self):
        return "/play/" + self.letter + "/" + self.filename

    def review_url(self):
        return "/review/" + self.letter + "/" + self.filename

    def file_url(self):
        return "/file/" + self.letter + "/" + self.filename

    def attributes_url(self):
        return "/attributes/" + self.letter + "/" + self.filename

    def phys_path(self):
        return os.path.join(SITE_ROOT + self.download_url())

    def screenshot_phys_path(self):
        """ Returns the physical path to the preview image. If the file has no
        preview image set or is using a shared screenshot, return an empty
        string.
        """
        SPECIAL_SCREENSHOTS = ["zzm_screenshot.png"]
        if self.screenshot and self.screenshot not in SPECIAL_SCREENSHOTS:
            return os.path.join(STATIC_PATH, "images/screenshots/{}/{}".format(
                self.letter, self.screenshot
            ))
        else:
            return ""

    def screenshot_url(self):
        SPECIAL_SCREENSHOTS = ["zzm_screenshot.png"]
        if self.screenshot and self.screenshot not in SPECIAL_SCREENSHOTS:
            return "images/screenshots/{}/{}".format(
                self.letter, self.screenshot
            )
        elif self.screenshot:  # Special case
            return "images/screenshots/{}".format(self.screenshot)
        else:
            return "images/screenshots/no_screenshot.png"

    def article_url(self):
        return "/article/" + self.letter + "/" + self.filename

    def wiki_url(self):
        return "http://zzt.org/zu/wiki/" + self.title

    def get_detail_ids(self):
        details = self.details.all()
        output = []
        for detail in details:
            output.append(int(detail.id))
        return output

    def author_list(self):
        return self.author.split("/")

    def company_list(self):
        return self.company.split("/")

    def genre_list(self):
        return self.genre.split("/")

    def language_list(self):
        short = self.language.split("/")
        return ", ".join(map(LANGUAGES.get, short))

    def ssv_list(self, attr):
        return getattr(self, attr).split("/")

    def ssv_links(self, attr, url):
        output = ""
        array = self.ssv_list(attr)
        for i in array:
            output += '<a href="{}">{}</a>, '.format(url, i)
        return output

    def is_lost(self):
        lost = self.details.all().values_list("id", flat=True)
        return True if DETAIL_LOST in lost else False

    def is_uploaded(self):
        uploaded = self.details.all().values_list("id", flat=True)
        return True if DETAIL_UPLOADED in uploaded else False

    def is_utility(self):
        utility = self.details.all().values_list("id", flat=True)
        return True if DETAIL_UTILITY in utility else False

    def is_zig(self):
        zig = self.details.all().values_list("id", flat=True)
        return True if DETAIL_ZIG in zig else False

    def is_zzt(self):
        zzt = self.details.all().values_list("id", flat=True)
        return True if DETAIL_ZZT in zzt else False

    def is_super_zzt(self):
        szzt = self.details.all().values_list("id", flat=True)
        return True if DETAIL_SZZT in szzt else False

    def is_zzm(self):
        zzm = self.details.all().values_list("id", flat=True)
        return True if DETAIL_ZZM in zzm else False

    def is_featured_world(self):
        featured = self.details.all().values_list("id", flat=True)
        return True if DETAIL_FEATURED in featured else False

    def supports_zeta_player(self):
        output = False
        if self.is_zzt():
            output = True
        elif self.is_super_zzt():
            output = True

        # Forcibly Restrict Zeta via a specific config
        if self.zeta_config and self.zeta_config.id == ZETA_RESTRICTED:
            output = False

        return output

    def calculate_article_count(self):
        if self.id is not None:
            self.article_count = self.articles.all().exclude(
                published=Article.REMOVED
            ).count()

    def calculate_reviews(self):
        # Calculate Review Count
        if self.id is not None:
            self.review_count = Review.objects.filter(zfile_id=self.id).count()

        # Calculate Rating
        if self.id is not None:
            ratings = Review.objects.filter(
                zfile_id=self.id, rating__gte=0
            ).aggregate(Avg("rating"))
            if ratings["rating__avg"] is not None:
                self.rating = round(ratings["rating__avg"], 2)

    def calculate_checksum(self, path=None):
        # Calculate an md5 checksum of the zip file
        if path is None:
            path = self.phys_path()
        try:
            with open(path, "rb") as fh:
                m = hashlib.md5()
                while True:
                    byte_stream = fh.read(102400)
                    m.update(byte_stream)
                    if not byte_stream:
                        break
        except FileNotFoundError:
            return False

        self.checksum = m.hexdigest()
        return True

    def calculate_boards(self):
        self.playable_boards = None
        self.total_boards = None
        temp_playable = 0
        temp_total = 0
        zip_path = self.phys_path()
        temp_path = os.path.join(SITE_ROOT, "temp")

        try:
            zf = zipfile.ZipFile(zip_path)
        except (FileNotFoundError, zipfile.BadZipFile):
            print("Skipping due to bad zip")
            return False

        file_list = zf.namelist()

        for file in file_list:
            name, ext = os.path.splitext(file)
            ext = ext.upper()

            if file.startswith("__MACOSX"):  # Don't count OSX info files
                continue

            if ext == ".ZZT":  # ZZT File
                # Extract the file
                try:
                    zf.extract(file, path=temp_path)
                except Exception:
                    print("Could not extract {}. Aborting.".format(file))
                    return False
            else:
                continue

            z = zookeeper.Zookeeper(
                os.path.join(temp_path, file)
            )

            to_explore = []
            accessible = []

            # Start with the starting board
            to_explore.append(z.world.current_board)

            false_positives = 0
            for idx in to_explore:
                # Make sure the board idx exists in the file
                # (in case of imported boards with passages)
                if idx >= len(z.boards):
                    false_positives += 1
                    continue

                # print(to_explore)
                # This board is clearly accessible
                accessible.append(idx)

                # Get the connected boards via edges
                if (
                    z.boards[idx].board_north != 0 and
                    z.boards[idx].board_north not in to_explore
                ):
                    to_explore.append(z.boards[idx].board_north)
                if (
                    z.boards[idx].board_south != 0 and
                    z.boards[idx].board_south not in to_explore
                ):
                    to_explore.append(z.boards[idx].board_south)
                if (
                    z.boards[idx].board_east != 0
                    and z.boards[idx].board_east not in to_explore
                ):
                    to_explore.append(z.boards[idx].board_east)
                if (
                    z.boards[idx].board_west != 0
                    and z.boards[idx].board_west not in to_explore
                ):
                    to_explore.append(z.boards[idx].board_west)

                # Get the connected boards via passages
                for stat in z.boards[idx].stats:
                    # print("ON BOARD IDX", idx)
                    try:
                        stat_name = z.boards[idx].get_element(
                            (stat.x, stat.y)
                        ).name
                        if stat_name == "Passage":
                            # print("Found a passage at", stat.x, stat.y)
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
            os.remove(os.path.join(temp_path, file))

        # Use null instead of 0 to avoid showing up in searches w/ board limits
        if self.playable_boards == 0:
            self.playable_boards = None
        else:
            self.playable_boards = temp_playable
        if self.total_boards == 0:
            self.total_boards = None
        else:
            self.total_boards = temp_total

        return True

    def calculate_size(self):
        self.size = os.path.getsize(self.phys_path())

    def supported_actions(self):
        features = {
            "download": False,
            "play": False,
            "view": False,
            "review": False,
            "article": False
        }

        # Download
        if self.file_exists():
            features["download"] = True

        # Play
        if features["download"] and (self.is_zzt() or self.is_super_zzt()):
            features["play"] = True

        # View
        if features["download"]:
            features["view"] = True

        # Review
        if features["download"] and self.can_review:
            features["review"] = True

        # Article
        features["article"] = True

        return features

    def generate_screenshot(
        self, world=None, board=0, font=None, filename=None
    ):
        # Get zip contents
        zf = zipfile.ZipFile(self.phys_path())

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

        # Name the screenshot
        if filename is None:
            self.screenshot = self.filename[:-4] + ".png"
        else:
            self.screenshot = filename

        # Extract the file and render
        try:
            zf.extract(world, path=SITE_ROOT + "/museum_site/static/data/")
        except NotImplementedError:
            return False
        z = zookeeper.Zookeeper(SITE_ROOT + "/museum_site/static/data/" + world)
        z.boards[board].screenshot(
            self.screenshot_phys_path()[:-4],
            title_screen=(not bool(board))
        )

        self.save()

        # Delete the extracted world
        # TODO: This leaves lingering folders for zips in folders
        os.remove(SITE_ROOT + "/museum_site/static/data/" + world)

        # Optimize the image
        optimize_image(self.screenshot_phys_path())

        return True

    def get_zip_info(self):
        try:
            zfh = zipfile.ZipFile(self.phys_path())
        except FileNotFoundError:
            return []
        return zfh.infolist()

    @property
    def identifier(self):
        return self.letter + "/" + self.filename


    def links(self):
        # Defaults
        output = {
            "download": {
                "visible": True,
                "text": "Download",
                "url": self.download_url,
                "classes": [],
            },
            "play": {
                "visible": True,
                "text": "Play Online",
                "url": self.play_url,
                "classes": [],
            },
            "view": {
                "visible": True,
                "text": "View Files",
                "url": self.file_url,
                "classes": [],
            },
            "review": {
                "visible": True,
                "text": "Reviews ({})".format(self.review_count),
                "url": self.review_url,
                "classes": [],
            },
            "article": {
                "visible": True,
                "text": "Articles ({})".format(self.article_count),
                "url": self.article_url,
                "classes": [],
            },
            "attributes": {
                "visible": True,
                "text": "Attributes",
                "url": self.attributes_url,
                "classes": [],
            },
        }

        # Modifiers
        # Multiple Downloads
        if self.downloads.count():
            output["download"]["text"] = "Downloads…"
            output["download"]["url"] = "/download/{}".format(self.identifier)

        # Explicit
        if self.explicit:
            output["download"]["classes"].append(" explicit")
            output["play"]["classes"].append(" explicit")
            output["view"]["classes"].append(" explicit")

        # Missing File
        if self.is_lost():
            output["download"]["visibile"] = False
            output["play"]["visibile"] = False
            output["view"]["visible"] = False

        # Unsupported Play Online Functionality
        if (not self.supports_zeta_player()) and self.archive_name == "":
            output["play"]["visible"] = False
        # Exception for uploads
        if (self.is_uploaded()):
            output["play"]["visible"] = True

        # Unpublished file
        if self.is_uploaded():
            output["review"]["visible"] = False

        # No Articles
        if self.article_count < 1:
            output["article"]["visible"] = False
        return output

    def overview(self):
        # Defaults
        output = {
            "basic": [
                {
                    "visible": True,
                    "label": "Author",
                    "value": self.ssv_links("author", "---"),
                    "classes": [],
                },
                {
                    "visible": True,
                    "label": "Company",
                    "value": self.ssv_links("company", "---"),
                    "classes": [],
                },
                {
                    "visible": True,
                    "label": "Released",
                    "value": date(self.release_date),
                    "classes": [],
                },
                {
                    "visible": True,
                    "label": "Genre",
                    "value": self.ssv_links("genre", "---"),
                    "classes": [],
                },
                {
                    "visible": True,
                    "label": "Filename",
                    "value": self.filename,
                    "classes": [],
                },
                {
                    "visible": True,
                    "label": "Size",
                    "value": filesizeformat(self.size),
                    "classes": [],
                },
            ],
        }
        return output


    def release_year(self):
        if self.release_date is None:
            return ""
        else:
            return str(self.release_date)[:4]

    # New functions for future revisions
    """
    def get_preview_image_url(self):
        if self.preview_image
            if self.preview_image not in SPECIAL_SCREENSHOTS:
                return STATIC_URL,
            else:  # Special cases
        else:  # Default
    """

"""
return os.path.join(STATIC_PATH, "images/screenshots/{}/{}".format(
                self.letter, self.screenshot
            ))
"""

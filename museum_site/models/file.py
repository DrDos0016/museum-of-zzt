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
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

try:
    import zookeeper
    HAS_ZOOKEEPER = True
except ImportError:
    HAS_ZOOKEEPER = False

from museum.settings import STATIC_URL

from museum_site.common import (
    slash_separated_sort, zipinfo_datetime_tuple_to_str, UPLOAD_CAP,
    STATIC_PATH, optimize_image, epoch_to_unknown, record,
    redirect_with_querystring
)
from museum_site.constants import SITE_ROOT, ZETA_RESTRICTED, LANGUAGES
from museum_site.models.review import Review
from museum_site.models.article import Article

from museum_site.models.base import BaseModel

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
    def advanced_search(self, p):
        qs = self.all()

        # Filter by simple fields
        for f in ["title", "author", "filename", "company", "genre"]:
            if p.get(f):
                field = "{}__icontains".format(f)
                value = p[f]
                qs = qs.filter(**{field: value})

        # Filter by language
        if p.get("lang"):
            if p["lang"] == "non-english":
                qs = qs.exclude(language="en")
            else:
                qs = qs.filter(language__icontains=p["lang"])

        # Filter by release year
        if p.get("year"):
            year = p["year"]
            if year == "Unk":  # Unknown release year
                qs = qs.filter(release_date=None)
            else:  # Numeric years
                qs = qs.filter(
                    release_date__gte="{}-01-01".format(year),
                    release_date__lte="{}-12-31".format(year),
                )

        # Filter by rating
        if p.get("min") and float(p["min"]) > 0:
            qs = qs.filter(rating__gte=float(p["min"]))
        if p.get("max") and float(p["max"]) < 5:
            qs = qs.filter(rating__lte=float(p["max"]))

        # Filter by playable/total board counts
        if p.get("board_min") and int(p["board_min"]) > 0:
            field = p.get("board_type", "total") + "_boards__gte"
            qs = qs.filter(**{field: int(p["board_min"])})
        if p.get("board_max") and int(p["board_max"]) <= 32767:
            field = p.get("board_type", "total") + "_boards__lte"
            qs = qs.filter(**{field: int(p["board_max"])})

        # Filter by items with/without reviews
        if p.get("reviews") == "yes":
            qs = qs.filter(review_count__gt=0)
        elif p.get("reviews") == "no":
            qs = qs.filter(review_count=0)

        # Filter by items with/without articles
        if p.get("articles") == "yes":
            qs = qs.filter(article_count__gt=0)
        elif p.get("articles") == "no":
            qs = qs.filter(article_count=0)

        # Filter by details
        if p.get("details"):
            qs = qs.filter(details__id__in=p.getlist("details"))

        qs = qs.distinct()
        return qs

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
            return self.filter(letter=letter, filename__startswith=filename)

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
        if p.get("q"):
            return File.objects.basic_search(p["q"])
        else:
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
            ).exclude(explicit=True).first()

        return zgame

    def roulette(self, rng_seed, limit):
        details = [DETAIL_ZZT, DETAIL_SZZT]

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
            Q(explicit=True)
        )

    def featured_worlds(self):
        return self.filter(details=DETAIL_FEATURED)

    """ TODO: Move this to something more generic than File objects """
    def reach(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None


class File(BaseModel):
    """ File object repesenting an upload to the site """
    objects = FileManager()
    model_name = "File"
    table_fields = [
        "DL", "Title", "Author", "Company", "Genre", "Date", "Rating"
    ]
    sort_options = [
        {"text": "Title", "val": "title"},
        {"text": "Author", "val": "author"},
        {"text": "Company", "val": "company"},
        {"text": "Rating", "val": "rating"},
        {"text": "Release Date (Newest)", "val": "-release"},
        {"text": "Release Date (Oldest)", "val": "release"}
    ]
    sort_keys = {
        "title": "sort_title",
        "author": "author",
        "company": "company",
        "rating": "-rating",
        "release": "release_date",
        "-release": "-release_date",
        "uploaded": "-id",
        "id": "id",
        "-id": "-id",
        "-publish_date": "-publish_date"
    }
    actions = None  # Populated by self.get_actions()

    SPECIAL_SCREENSHOTS = ["zzm_screenshot.png"]
    PREFIX_UNPUBLISHED = "UNPUBLISHED FILE - This file's contents have not \
    been fully checked by staff."
    ICONS = {
        "explicit": {"glyph": "🔞", "title": "This file contains explicit content.", "role":"explicit-icon"},
        "unpublished": {"glyph": "🚧", "title": "This file is unpublished. Its contents have not been fully checked by staff.", "role":"unpub-icon"},
        "featured": {"glyph": "🗝️", "title": "This file is a featured world.", "role":"fg-icon"},
        "lost": {"glyph": "❌", "title": "This file is a known to be lost. No download is available.", "role":"lost-icon"},
    }

    REVIEW_NO = 0
    REVIEW_APPROVAL = 1
    REVIEW_YES = 2

    REVIEW_LEVELS = (
        (REVIEW_NO, "Can't Review"),
        (REVIEW_APPROVAL, "Requires Approval"),
        (REVIEW_YES, "Can Review"),
    )

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
    key = models.CharField(max_length=50, db_index=True, default="")
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
    can_review = models.IntegerField(default=REVIEW_YES, choices=REVIEW_LEVELS)
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
            "explicit": int(self.explicit),
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

    def file_exists(self):
        return True if os.path.isfile(self.phys_path()) else False

    def play_url(self):
        return "/play/{}/{}/".format(self.letter, self.key)

    def review_url(self):
        return "/review/{}/{}/".format(self.letter, self.key)

    def file_url(self):
        return "/file/{}/{}/".format(self.letter, self.key)

    def attributes_url(self):
        return "/attributes/{}/{}/".format(self.letter, self.key)

    def tool_url(self):
        return "/tools/{}/{}".format(self.letter, self.filename)

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
        return "/article/{}/{}/".format(self.letter, self.key)

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

    def ssv_list(self, attr, lookup=None):
        if lookup is None:
            return getattr(self, attr).split("/")
        else:
            return [lookup.get(i, i) for i in getattr(self, attr).split("/")]

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

        # Normally only ZZT/SZZT files should work
        if self.is_zzt() or self.is_super_zzt():
            output = True

        # Incorrectly assume uploaded files will work
        if self.is_uploaded():
            output = True

        # Forcibly Restrict Zeta via a specific config (applies to uploads as well)
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
            record("Skipping Calculate Boards function due to bad zip")
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
                    record("Could not extract {}. Aborting.".format(file))
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

                # record(to_explore)
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
                    # record("ON BOARD IDX", idx)
                    try:
                        stat_name = z.boards[idx].get_element(
                            (stat.x, stat.y)
                        ).name
                        if stat_name == "Passage":
                            # record("Found a passage at", stat.x, stat.y)
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

    def init_actions(self):
        """ Determine which actions may be performed on this zfile """
        self.actions = {
            "download": False,
            "play": False,
            "view": False,
            "review": False,
            "article": False
        }

        # Download
        if self.file_exists():
            self.actions["download"] = True

        # Play
        if self.archive_name or (
            self.actions["download"] and self.supports_zeta_player()
        ):
            self.actions["play"] = True

        # View
        if self.actions["download"]:
            self.actions["view"] = True

        # Review
        if (self.actions["download"] and self.can_review) or self.review_count:
            self.actions["review"] = True
        if self.actions["review"] and self.is_uploaded():
            self.actions["review"] = False

        # Article
        if self.article_count:
            self.actions["article"] = True

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

    def release_year(self, default=""):
        if self.release_date is None:
            return default
        else:
            return str(self.release_date)[:4]

    def url(self):
        # For files, the file viewer is considered the file's URL
        return "/file/{}/{}/".format(self.letter, self.key)

    def preview_url(self):
        if self.screenshot:
            if self.screenshot not in self.SPECIAL_SCREENSHOTS:
                return os.path.join(
                    STATIC_URL, "images/screenshots/{}/{}".format(
                        self.letter, self.screenshot)
                )
            else:
                return os.path.join(
                    STATIC_URL, "images/screenshots/{}".format(self.screenshot)
                )
        else:
            return os.path.join(
                    STATIC_URL, "images/screenshots/no_screenshot.png"
                )

    @mark_safe
    def rating_str(self, show_maximum=True):
        if self.rating is not None:
            long_rating = (str(self.rating) + "0")[:4]
            if show_maximum:
                return "{} / 5.00".format(long_rating)
            else:
                return long_rating
        else:
            return "<i>No rating</i>"

    @mark_safe
    def publish_date_str(self):
        if (
            (self.publish_date is None) or
            (self.publish_date.strftime("Y-m-d") < "2018-11-07")
        ):
            return "<i>Unknown</i>"
        return self.publish_date.strftime("%b %d, %Y, %I:%M:%S %p")

    @mark_safe
    def boards_str(self):
        return "{} / {}".format(self.playable_boards, self.total_boards)

    @mark_safe
    def details_str(self):
        output = ""
        for i in self.details.all():
            output += i.detail + ", "
        return output[:-2]

    @mark_safe
    def details_links(self):
        output = ""
        for i in self.details.all():
            output += '<a href="{}">{}</a>, '.format(i.url(), i.detail)
        return output[:-2]

    def language_pairs(self):
        language_list = self.language.split("/")
        output = []

        for i in language_list:
            output.append((LANGUAGES.get(i, i), i))
        return output

    def links(self, debug=False):
        links = []

        if self.actions is None:
            self.init_actions()

        # Download
        if self.actions["download"]:
            if self.downloads.count():
                value = "Downloads…"
                url = "/download/{}/{}".format(self.letter, self.key)
            else:
                value = "Download"
                url=self.download_url()

            link = {"datum": "link", "value":value, "url":url, "roles":["download-link"], "icons":self.get_all_icons()}
        else:
            link = {"datum": "text", "value":"Download", "kind":"faded"}

        links.append(link)


        # Play Online
        if self.actions["play"]:
            link = {"datum": "link", "value":"Play Online", "url":self.play_url(), "roles":["play-link"], "icons":self.get_major_icons()}
        else:
            link = {"datum": "text", "value":"Play Online", "kind":"faded"}
        links.append(link)

        # View Files
        if self.actions["view"]:
            link = {"datum": "link", "value":"View Files", "url": self.file_url(), "roles":["view-link"], "icons":self.get_major_icons()}
        else:
            link = {"datum": "text", "value":"View Files", "kind":"faded"}
        links.append(link)

        # Reviews
        if self.actions["review"]:
            link = {"datum": "link", "value":"Reviews ({})".format(self.review_count), "url":self.review_url(), "roles":["review-link"]}
        else:
            link = {"datum": "text", "value":"Reviews (0)", "kind":"faded"}
        links.append(link)

        # Articles
        if self.actions["article"]:
            link = {"datum": "link", "value":"Articles ({})".format(self.article_count), "url":self.article_url(), "roles":["article-link"]}
        else:
            link = {"datum": "text", "value":"Articles (0)", "kind":"faded"}
        links.append(link)

        # Attributes
        link = {"datum": "link", "value":"Attributes", "url":self.attributes_url(), "roles":["attribute-link"]}
        links.append(link)

        if debug:
            link = {"datum": "link", "value":"Edit ZF#{}".format(self.id), "url":self.admin_url(), "roles":["debug-link"], "kind":"debug"}
            links.append(link)
            link = {"datum": "link", "value":"Tools ZF#{}".format(self.id), "url":self.tool_url(), "roles":["debug-link"], "kind":"debug"}
            links.append(link)

        return links

    def initial_context(self, *args, **kwargs):
        context = super(File, self).initial_context(*args, **kwargs)
        context["hash_id"] = self.filename

        if hasattr(self, "extra_context"):
            context.update(self.extra_context)

        # Append roles/extras based on details
        if self.explicit:
            context["roles"].append("explicit")
        if self.is_uploaded():
            context["roles"].append("unpublished")
        if self.is_featured_world():
            context["roles"].append("featured")
            context["extras"].append("museum_site/blocks/extra-featured-world.html")
            context["featured_articles"] = self.articles.filter(category="Featured Game").defer("content").order_by("-publish_date")
        if self.is_lost():
            context["roles"].append("lost")
            if self.description:
                context["extras"].append("museum_site/blocks/extra-lost.html")
                context["lost_description"] = self.description
        if self.is_utility() and self.description:
            context["extras"].append("museum_site/blocks/extra-utility.html")
            context["utility_description"] = self.description


        return context

    def detailed_block_context(self, extras=None, *args, **kwargs):
        """ Return info to populate a detail block """
        context = self.initial_context(*args, **kwargs)
        context.update(
            tag={"opening": "div", "closing": "/div"},
            columns=[],
            title={"datum": "title", "value":self.title, "url":self.url(), "icons":self.get_all_icons()},
        )

        # Prepare Columns
        context["columns"].append([
            {"datum": "ssv-links", "label": "Author"+("s" if len(self.ssv_list("author")) > 1 else ""), "values":self.ssv_list("author"), "url":"/search/?author="},
            {"datum": "ssv-links", "label":"Compan"+("ies" if len(self.ssv_list("company")) > 1 else "y"), "values":self.ssv_list("company"), "url":"/search/?company="},
            {"datum": "link", "label":"Released", "value":(self.release_date or "Unknown"), "url":"/search/?year={}".format(self.release_year(default="unk"))},
            {"datum": "ssv-links", "label": "Genre"+("s" if len(self.ssv_list("genre")) > 1 else ""), "values":self.ssv_list("genre"), "url":"/search/?genre="},
            {"datum": "text", "label": "Filename", "value":self.filename},
            {"datum": "text", "label": "Size", "value":filesizeformat(self.size)},
        ])

        context["columns"].append([
            {"datum": "text", "label": "Details", "value":self.details_links()},
            {"datum": "text", "label":"Rating", "value":self.rating_str(), "title":"Based on {} review{}".format(self.review_count, "s" if self.review_count != 1 else "")},
            {"datum": "text", "label":"Boards", "value":self.boards_str(), "title":"Playable/Total Boards. Values are not 100% accurate." if self.total_boards else ""},
            {"datum": "language-links", "label":"Language"+("s" if len(self.ssv_list("language")) > 1 else ""), "values":self.language_pairs(), "url":"/search/?lang="},

        ])

        if self.is_uploaded() and self.upload_set.first():
            context["columns"][1].append({"datum": "text", "label":"Upload Date", "value":self.upload_set.first().date})
        if not self.is_uploaded() and self.publish_date:
            context["columns"][1].append({"datum": "text", "label":"Publish Date", "value":self.publish_date_str()})

        # Prepare Links
        context["links"] = self.links(context["debug"])

        if context["debug"]:
            context["columns"][1].append(
                {
                    "datum": "multi-link",
                    "roles":["debug-link"], "kind":"debug",
                    "label": "Debug",
                    "values":[
                        {"url": self.admin_url(), "text": "Edit"},
                        {"url": self.tool_url(), "text": "Tools"},
                    ]
                }
            )
        return context

    def list_block_context(self, extras=None, *args, **kwargs):
        context = super(File, self).initial_context()
        context.update(self.initial_context(view="list"))

        # Prepare Links
        cells = []
        if self.actions is None:
            self.init_actions()

        if self.actions["download"]:
            link = {"datum": "link", "value":"DL", "url":self.download_url(), "tag":"td",
                    "icons":self.get_all_icons()}
        else:
            link = {"datum": "text", "value":"DL", "kind":"faded", "tag":"td"}
        cells.append(link)

        if self.actions["view"]:
            link = {"datum": "link", "value":self.title, "url":self.url(), "tag":"td",
                "icons":self.get_all_icons()}
        else:
            link = {"datum": "text", "value":self.title, "tag":"td", "kind":"faded"}
        cells.append(link)


        cells.append({"datum": "ssv-links", "values":self.ssv_list("author"), "url":"/search/?author=", "tag":"td"})
        cells.append({"datum": "ssv-links", "values":self.ssv_list("company"), "url":"/search/?company=", "tag":"td"})
        cells.append({"datum": "ssv-links", "values":self.ssv_list("genre"), "url":"/search/?genre=", "tag":"td"})
        cells.append({"datum": "link", "value":(self.release_date or "Unknown"), "url":"/search/?year={}".format(self.release_year(default="unk")), "tag":"td"})
        cells.append({"datum": "text", "value":self.rating_str(show_maximum=False) if self.rating else "—", "tag":"td"})

        # Modify download text if needed
        if self.downloads.count():
            cells[0]["value"] = "DLs…"
            cells[0]["url"] = "/download/{}".format(
                self.identifier
            )

        context.update(cells=cells)
        return context

    def gallery_block_context(self, extras=None, *args, **kwargs):
        context = super(File, self).initial_context()
        context.update(self.initial_context(view="gallery"))

        # Prepare Links
        if self.actions is None:
            self.init_actions()

        if self.actions["view"]:
            title_datum = {"datum": "title", "value":self.title, "url":self.url(), "icons":self.get_all_icons()}
        else:
            title_datum = {"datum": "text", "value":self.title, "kind":"faded"}

        context.update(
            preview=dict(url=self.preview_url, alt=self.preview_url),
            title=title_datum,
            columns=[],
        )

        context["columns"].append([
            {"datum": "ssv-links", "values":self.ssv_list("author"), "url":"/search/?author="}
        ])

        return context

    def title_datum_context(self):
        # Returns a context for displaying the ZFile's title datum
        context = {"datum": "title", "tag":"h1", "value":self.title, "icons":self.get_all_icons()}
        return context

    def _init_icons(self):
        # Populates major and minor icons for file
        self._minor_icons = []
        self._major_icons = []

        if self.explicit:
            self._major_icons.append(File.ICONS["explicit"])
        if self.is_uploaded():
            self._major_icons.append(File.ICONS["unpublished"])
        if self.is_lost():
            self._major_icons.append(File.ICONS["lost"])
        if self.is_featured_world():
            self._minor_icons.append(File.ICONS["featured"])

    def get_all_icons(self):
        # Returns combined list of both major and minor icons, populating if needed
        if not hasattr(self, "_major_icons"):
            self._init_icons()
        return self._major_icons + self._minor_icons

    def get_major_icons(self):
        # Returns list of major icons, populating if needed
        if not hasattr(self, "_major_icons"):
            self._init_icons()
        return self._major_icons

import hashlib
import os
import subprocess
import zipfile
from datetime import datetime

from datetime import datetime

from django.db import models
from django.db.models import Avg

try:
    import zookeeper
    HAS_ZOOKEEPER = True
except ImportError:
    HAS_ZOOKEEPER = False

from .common import slash_separated_sort
from .constants import SITE_ROOT
from .review import Review

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


class File(models.Model):
    """ File object repesenting an upload to the site

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
    """

    letter = models.CharField(max_length=1, db_index=True)
    filename = models.CharField(max_length=50)
    title = models.CharField(max_length=80)
    sort_title = models.CharField(
        max_length=100, db_index=True, default="", blank=True,
        help_text="Leave blank to set automatically"
    )
    author = models.CharField(max_length=80)
    size = models.IntegerField(default=0)
    genre = models.CharField(max_length=80, blank=True, default="")
    release_date = models.DateField(default=None, null=True, blank=True)
    release_source = models.CharField(
        max_length=20, null=True, default=None, blank=True
    )
    screenshot = models.CharField(
        max_length=80, blank=True, null=True, default=None
    )
    company = models.CharField(
        max_length=80, default="", blank=True,
    )
    description = models.TextField(null=True, blank=True, default="")
    review_count = models.IntegerField(
        default=0, help_text="Set automatically. Do not adjust."
    )
    rating = models.FloatField(null=True, default=None, blank=True)
    details = models.ManyToManyField("Detail", default=None, blank=True)
    articles = models.ManyToManyField("Article", default=None, blank=True)
    article_count = models.IntegerField(
        default=0, help_text="Set automatically. Do not adjust."
    )
    checksum = models.CharField(max_length=32, null=True,
                                blank=True, default="")
    superceded = models.ForeignKey("File", db_column="superceded_id",
                                   null=True, blank=True, default=None,
                                   on_delete=models.SET_NULL)
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

    aliases = models.ManyToManyField("Alias", default=None, blank=True)
    upload_date = models.DateTimeField(
        null=True, auto_now_add=True, db_index=True, blank=True,
        help_text="Date File was uploaded to the Museum"
    )
    publish_date = models.DateTimeField(
        null=True, default=None, db_index=True, blank=True,
        help_text="Date File was published on the Museum"
    )
    last_modified = models.DateTimeField(
        auto_now=True,
        help_text="Date DB entry was last modified"
    )

    uploader_ip = models.GenericIPAddressField(
        null=True, blank=True, default=None, editable=False
    )

    zeta_config = models.ForeignKey("Zeta_Config", null=True, blank=True,
    default=None, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["sort_title", "letter"]

    def __str__(self):
        return "[" + str(self.id) + "] " + self.title

    def basic_save(self, *args, **kwargs):
        super(File, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Pre save
        # Force lowercase letter
        self.letter = self.letter.lower()

        # Sort genres
        self.genre = slash_separated_sort(self.genre)

        # Create sorted title
        self.sort_title = self.sorted_title()

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
            "upload_date": self.upload_date,
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

    def sorted_title(self):
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

        return sort_title

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
        if self.is_uploaded():
            return "/zgames/uploaded/" + self.filename
        else:
            return "/zgames/" + self.letter + "/" + self.filename

    def file_exists(self):
        return True if os.path.isfile(self.phys_path()) else False

    def play_url(self):
        return "/play/" + self.letter + "/" + self.filename

    def review_url(self):
        return "/review/" + self.letter + "/" + self.filename

    def file_url(self):
        return "/file/" + self.letter + "/" + self.filename

    def phys_path(self):
        return os.path.join(SITE_ROOT + self.download_url())

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

    def genre_list(self):
        return self.genre.split("/")

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
        lost = self.details.all().values_list("id", flat=True)
        return True if DETAIL_ZZT in lost else False

    def is_super_zzt(self):
        lost = self.details.all().values_list("id", flat=True)
        return True if DETAIL_SZZT in lost else False

    def supports_zeta_player(self):
        return (self.is_zzt() or self.is_super_zzt() or self.zeta_config is not None)

    def calculate_article_count(self):
        if self.id is not None:
            self.article_count = self.articles.all().filter(
                published=True
            ).count()

    def calculate_reviews(self):
        # Calculate Review Count
        if self.id is not None:
            self.review_count = Review.objects.filter(file_id=self.id).count()

        # Calculate Rating
        if self.id is not None:
            ratings = Review.objects.filter(
                file_id=self.id, rating__gte=0
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
        if self.is_uploaded():
            return False

        self.playable_boards = None
        self.total_boards = None
        temp_playable = 0
        temp_total = 0
        zip_path = os.path.join(SITE_ROOT, "zgames", self.letter, self.filename)
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
                except:
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
                if z.boards[idx].board_north != 0 and z.boards[idx].board_north not in to_explore:
                    to_explore.append(z.boards[idx].board_north)
                if z.boards[idx].board_south != 0 and z.boards[idx].board_south not in to_explore:
                    to_explore.append(z.boards[idx].board_south)
                if z.boards[idx].board_east != 0 and z.boards[idx].board_east not in to_explore:
                    to_explore.append(z.boards[idx].board_east)
                if z.boards[idx].board_west != 0 and z.boards[idx].board_west not in to_explore:
                    to_explore.append(z.boards[idx].board_west)

                # Get the connected boards via passages
                for stat in z.boards[idx].stats:
                    # print("ON BOARD IDX", idx)
                    try:
                        stat_name = z.boards[idx].get_element((stat.x, stat.y)).name
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

    def from_request(self, request, editing=False):
        upload_directory = os.path.join(SITE_ROOT, "zgames/uploaded")

        if request.method != "POST":
            return False

        # For editing, force the original zip's filename
        if str(request.FILES.get("file", "")):
            if not editing:
                self.filename = str(request.FILES.get("file"))
            self.size = int(request.FILES.get("file").size)

        self.title = request.POST.get("title")
        self.letter = self.letter_from_title()
        # sort_title handled by saving
        self.author = request.POST.get("author")
        self.release_date = request.POST.get("release_date")
        if self.release_date == "":
            self.release_date = None
        self.release_source = "User upload"
        self.company = request.POST.get("company", "")
        self.description = request.POST.get("desc", "")
        self.genre = "/".join(request.POST.getlist("genre"))
        self.publish_date = None
        self.uploader_ip = request.META["REMOTE_ADDR"]

        # SCREENSHOT -- Currently manual
        # DETAILS -- Currently manual
        # Check for a duplicate filename
        if str(request.FILES.get("file", "")):
            dupe = File.objects.filter(filename=self.filename)
            if dupe and (dupe[0].id != self.id):  # Replace the file for edits
                return {"status": "error",
                        "msg": "The chosen filename is already in use."}

            # Save the file to the uploaded folder
            file_path = os.path.join(upload_directory, self.filename)
            with open(file_path, 'wb+') as fh:
                for chunk in request.FILES["file"].chunks():
                    fh.write(chunk)

            # Check for unsupported compression
            zip_file = zipfile.ZipFile(os.path.join(file_path))
            files = zip_file.namelist()
            zip_info = zip_file.infolist()
            rezip = False
            for i in zip_info:
                if i.compress_type not in [
                    zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED
                ]:
                    rezip = True
                    break

            # Check if the file needs to be rezipped
            if rezip:
                None
                # TODO This feature should wait until the Museum is on a new server
                # print("I'm gonna rezip")

            # Calculate checksum
            self.calculate_checksum(file_path)

        # SITE META
        return {"status": "success"}

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
        if features["download"]:
            features["review"] = True

        # Article
        features["article"] = True

        return features

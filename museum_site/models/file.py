import hashlib
import html
import os
import zipfile

from urllib.parse import quote

from django.core.cache import cache
from django.contrib import admin
from django.db import models
from django.template.defaultfilters import filesizeformat
from django.utils.safestring import mark_safe

try:
    import zookeeper
    HAS_ZOOKEEPER = True
except ImportError:
    HAS_ZOOKEEPER = False

from museum.settings import STATIC_URL

from museum_site.common import zipinfo_datetime_tuple_to_str, record
from museum_site.constants import SITE_ROOT, LANGUAGES, STATIC_PATH
from museum_site.core.detail_identifiers import *
from museum_site.core.zeta_identifiers import *
from museum_site.core.image_utils import optimize_image
from museum_site.models.zfile_legacy import ZFile_Legacy
from museum_site.models.zfile_urls import ZFile_Urls
from museum_site.models.review import Review
from museum_site.models.article import Article
from museum_site.models.base import BaseModel
from museum_site.querysets.zfile_querysets import *


class File(BaseModel, ZFile_Urls, ZFile_Legacy):
    """ ZFile object repesenting an a file hosted on the Museum site """
    objects = ZFile_Queryset.as_manager()

    model_name = "File"
    table_fields = ["DL", "Title", "Author", "Company", "Genre", "Date", "Review"]
    sort_options = [
        {"text": "Title", "val": "title"},
        {"text": "Author", "val": "author"},
        {"text": "Company", "val": "company"},
        {"text": "Rating", "val": "rating"},
        {"text": "Release Date (Newest)", "val": "-release"},
        {"text": "Release Date (Oldest)", "val": "release"},
    ]
    sort_keys = {
        # Key - Value from <select> used in GET params
        # Value - Django order_by param
        "title": ["sort_title"],
        "author": ["authors__title", "sort_title"],
        "company": ["companies__title", "sort_title"],
        "rating": ["-rating", "sort_title"],
        "release": ["release_date", "sort_title"],
        "-release": ["-release_date", "sort_title"],
        "uploaded": ["-id"],
        "id": ["id"],
        "-id": ["-id"],
        "-publish_date": ["-publish_date", "sort_title"]
    }
    actions = None  # Populated by self.init_actions()
    detail_ids = None  # Populated by self.init_detail_ids()

    SPECIAL_SCREENSHOTS = ["zzm_screenshot.png"]
    PREFIX_UNPUBLISHED = "UNPUBLISHED FILE - This file's contents have not been fully checked by staff."
    ICONS = {
        "explicit": {"glyph": "🔞", "title": "This file contains explicit content.", "role": "explicit-icon"},
        "unpublished": {"glyph": "🚧", "title": "This file is unpublished. Its contents have not been fully checked by staff.", "role": "unpub-icon"},
        "featured": {"glyph": "🗝️", "title": "This file is a featured world.", "role": "fg-icon"},
        "lost": {"glyph": "❌", "title": "This file is a known to be lost. No download is available.", "role": "lost-icon"},
        "weave": {"glyph": "🧵", "title": "This file contains content designed for Weave ZZT.", "role": "weave-icon"},
    }

    (REVIEW_NO, REVIEW_APPROVAL, REVIEW_YES) = (0, 1, 2)
    REVIEW_LEVELS = (
        (REVIEW_NO, "Can't Review"),
        (REVIEW_APPROVAL, "Requires Approval"),
        (REVIEW_YES, "Can Review"),
    )

    # Fields
    letter = models.CharField(max_length=1, db_index=True, editable=False, help_text="Letter used for filtering browse pages")
    filename = models.CharField(max_length=50, help_text="Filename of the zip file containing this zfile's contents")
    key = models.CharField(max_length=50, db_index=True, default="", help_text="Unique identifier used for URLs and filtering. Filename w/out extension")
    size = models.IntegerField(default=0, editable=False, help_text="Size in bytes of the zip file")
    title = models.CharField(max_length=80, help_text="Canonical name of the release")
    release_date = models.DateField(default=None, null=True, blank=True, help_text="Release date of zip file's contents.")
    release_source = models.CharField(max_length=20, default="", blank=True, help_text="Source of release date when applicable.")
    language = models.CharField(
        max_length=50, default="en",
        help_text="Slash-separated list of languages required to comprehend the zip file's contents. ISO 639-1 code. List defined in constants.py"
    )
    description = models.TextField(
        blank=True, default="", help_text="Description of contents. Wrap in quotes if written by author, leave unquoted for unofficial descriptions."
    )
    playable_boards = models.IntegerField(
        null=True, blank=True, default=None,
        help_text="(Estimated) count of boards visitable during gameplay. Set automatically. Do not adjust."
    )
    total_boards = models.IntegerField(
        null=True, blank=True, default=None,
        help_text="Total number of boards contained in zip file. Set automatically. Do not adjust."
    )
    archive_name = models.CharField(
        max_length=80,
        default="",
        blank=True,
        help_text="Identifier used on archive.org mirrors. Typically the 'zzt_' + zip name w/out extension. (ex: zzt_burgerj)"
    )
    screenshot = models.CharField(
        max_length=80, blank=True, default="",
        help_text="Filename for preview image. /static/images/screenshots/&lt;letter&gt;/&lt;screenshot&gt;"
    )
    file_license = models.CharField(max_length=150, default="Unknown", help_text="License the file is released under.")
    license_source = models.CharField(max_length=150, default="", blank=True, help_text="Source of licensing information.")

    # Derived Data
    checksum = models.CharField(max_length=32, blank=True, default="", help_text="md5 checksum of zip file")
    sort_title = models.CharField(
        max_length=100, db_index=True, default="", blank=True,
        help_text="Autogenerated value for actual title sorting. Strips articles and pads numbers to use leading digits."
    )

    # Reviews
    review_count = models.IntegerField(
        default=0, editable=False, help_text="Cached number of review associated with this zip file. Set automatically. Do not adjust."
    )
    rating = models.FloatField(null=True, default=None, blank=True, help_text="Mean score based on all reviews with scores attached.")

    # Museum Properties
    explicit = models.BooleanField(default=False, help_text="Boolean to mark zfile as containing explicit content.")
    spotlight = models.BooleanField(default=True, help_text="Boolean to mark zfile as being suitable for display on the front page.")
    can_review = models.IntegerField(
        default=REVIEW_YES, choices=REVIEW_LEVELS, help_text="Choice of whether the file can be reviewed freely, pending approval, or not at all."
    )
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
    articles = models.ManyToManyField("Article", default=None, blank=True)
    article_count = models.IntegerField(default=0, editable=False, help_text="Cached number of articles associated with this zip file.")
    authors = models.ManyToManyField("Author", default=None, blank=True)
    companies = models.ManyToManyField("Company", default=None, blank=True)
    content = models.ManyToManyField("Content", default=None, blank=True)
    details = models.ManyToManyField("Detail", default=None, blank=True)
    downloads = models.ManyToManyField("Download", default=None, blank=True)
    genres = models.ManyToManyField("Genre", default=None, blank=True)
    zeta_config = models.ForeignKey("Zeta_Config", null=True, blank=True, default=1, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["sort_title", "letter"]

    def __str__(self):
        return "{} [{}][#{}]".format(self.title, self.key, self.id)

    # Populating functions
    def init_detail_ids(self):
        if self.detail_ids is None:
            self.detail_ids = self.details.all().values_list("id", flat=True)

    # Database functions
    def basic_save(self, *args, **kwargs):
        super(File, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Pre save
        # Force lowercase letter
        if not self.letter:
            self.letter = self.letter_from_title()
        else:
            self.letter = self.letter.lower()

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

    # Filepaths
    def phys_path(self): return os.path.join(SITE_ROOT + self.download_url())

    def screenshot_phys_path(self):
        """ Returns the physical path to the preview image. If the file has no preview image set or is using a shared screenshot, return an empty string. """
        if self.screenshot and self.screenshot not in self.SPECIAL_SCREENSHOTS:
            return os.path.join(STATIC_PATH, "images/screenshots/{}/{}".format(
                self.letter, self.screenshot
            ))
        else:
            return ""

    # Other Functions
    def jsoned(self):
        data = {
            "letter": self.letter,
            "filename": self.filename,
            "title": self.title,
            "sort_title": self.sort_title,
            "author": self.author_list(),
            "size": self.size,
            "genres": self.genre_list(),
            "release_date": self.release_date,
            "release_source": self.release_source,
            "screenshot": self.screenshot,
            "company": self.get_related_list("companies", "title"),
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
            data["details"].append({"id": d.id, "detail": d.title})

        for a in self.articles.all().only("id", "title"):
            data["articles"].append({"id": a.id, "title": a.title})

        for a in self.aliases.all():
            data["aliases"].append({"id": a.id, "alias": a.alias})

        return data

    def calculate_sort_title(self):
        output = ""
        # Handle titles that start with A/An/The
        sort_title = self.title.lower()

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

        self.sort_title = output
        return True

    def letter_from_title(self):
        """ Returns the letter a file should be listed under after removing (a/an/the) """
        title = self.title.lower()
        for eng_article in ["a ", "an ", "the "]:
            if title.startswith(eng_article):
                title = title.replace(eng_article, "", 1)

        return title[0] if title[0] in "abcdefghijklmnopqrstuvwxyz" else "1"

    def file_exists(self): return True if os.path.isfile(self.phys_path()) else False

    def author_list(self):
        output = []
        for a in self.authors.all():
            output.append(a.title)
        return output

    def genre_list(self):
        output = []
        for g in self.genres.all():
            output.append(g.title)
        return output

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

    def is_lost(self):  # Used in file-review.html
        self.init_detail_ids()
        return True if DETAIL_LOST in self.detail_ids else False

    def is_uploaded(self):  # Used in file-review.html
        self.init_detail_ids()
        return True if DETAIL_UPLOADED in self.detail_ids else False

    def is_weave(self):  # Used in file.html
        self.init_detail_ids()
        return True if DETAIL_WEAVE in self.detail_ids else False

    def is_detail(self, detail_id):
        self.init_detail_ids()
        self.init_detail_ids()
        return True if detail_id in self.detail_ids else False

    def supports_zeta_player(self):
        output = False

        # Normally only ZZT/SZZT/Weave files should work
        if self.is_detail(DETAIL_ZZT) or self.is_detail(DETAIL_SZZT) or self.is_detail(DETAIL_WEAVE):
            output = True

        # Incorrectly assume uploaded files will work
        if self.is_detail(DETAIL_UPLOADED):
            output = True

        # Forcibly Restrict Zeta via a specific config (applies to uploads as well)
        if self.zeta_config_id and self.zeta_config_id == ZETA_RESTRICTED:
            output = False

        return output

    def calculate_article_count(self):
        if self.id is not None:
            self.article_count = self.articles.all().exclude(published=Article.REMOVED).count()

    def calculate_reviews(self):
        # Calculate Review Count
        if self.id is not None:
            self.review_count = Review.objects.for_zfile(self.id).count()

        # Calculate Rating
        if self.id is not None:
            ratings = Review.objects.average_rating_for_zfile(self.id)
            self.rating = None if ratings["rating__avg"] is None else round(ratings["rating__avg"], 2)

    def calculate_checksum(self, path=None, set_to_results=True):
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

        checksum = m.hexdigest()
        if set_to_results:
            self.checksum = checksum
        return checksum

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
        self.actions = {"review": False}
        self.actions["download"] = True if self.file_exists() else False
        self.actions["view"] = True if self.actions["download"] else False
        self.actions["play"] = True if self.archive_name or (self.actions["download"] and self.supports_zeta_player()) else False
        self.actions["article"] = True if self.article_count else False
        # Review
        if (self.actions["download"] and self.can_review) or self.review_count:
            self.actions["review"] = True
        if self.actions["review"] and self.is_detail(DETAIL_UPLOADED):
            self.actions["review"] = False

    def generate_screenshot(self, world=None, board=0, font=None, filename=None):
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
        if filename is None or filename == "":
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

    def release_year(self, default=""): return default if self.release_date is None else str(self.release_date)[:4]

    @mark_safe
    def rating_str(self, show_maximum=True):
        if self.rating is not None:
            long_rating = (str(self.rating) + "0")[:4]
            if show_maximum:
                return "{} / 5.00".format(long_rating)
            return long_rating
        return "<i>No rating</i>"

    @mark_safe
    def publish_date_str(self):
        if (self.publish_date is None) or (self.publish_date.strftime("%Y-%m-%d") < "2018-11-07"):
            return "<i>Unknown</i>"
        return self.publish_date.strftime("%b %d, %Y, %I:%M:%S %p")

    @mark_safe
    def boards_str(self):
        return "{} / {}".format(self.playable_boards, self.total_boards)

    @mark_safe
    def details_links(self):
        output = ""
        for i in self.details.visible():
            output += '<a href="/file/browse/detail/{}/">{}</a>, '.format(i.slug, i.title)
        return output[:-2]

    @mark_safe
    def author_links(self):
        output = ""
        for i in self.authors.all():
            output += '<a href="/file/browse/author/{}/">{}</a>, '.format(quote(i.slug, safe=""), html.escape(i.title))
        return output[:-2]

    @mark_safe
    def genre_links(self):
        output = ""
        for i in self.genres.all():
            output += '<a href="/file/browse/genre/{}/">{}</a>, '.format(quote(i.slug, safe=""), html.escape(i.title))
        return output[:-2]

    @mark_safe
    def company_links(self):
        output = ""
        for i in self.companies.all():
            output += '<a href="/file/browse/company/{}/">{}</a>, '.format(quote(i.slug, safe=""), html.escape(i.title))
        return output[:-2]

    def language_pairs(self):
        language_list = self.language.split("/")
        output = []

        for i in language_list:
            output.append((LANGUAGES.get(i, i), i))
        return output

    @mark_safe
    def language_links(self):
        output = ""
        for i in self.language_pairs():
            output += '<a href="/file/browse/language/{}/">{}</a>, '.format(quote(i[1], safe=""), html.escape(i[0]))
        return output[:-2]

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
                url = self.download_url()

            link = {"datum": "link", "value": value, "url": url, "roles": ["download-link"], "icons": self.get_all_icons()}
        else:
            link = {"datum": "text", "value": "Download", "kind": "faded"}

        links.append(link)

        # Play Online
        if self.actions["play"]:
            link = {"datum": "link", "value": "Play Online", "url": self.play_url(), "roles": ["play-link"], "icons": self.get_major_icons()}
        else:
            link = {"datum": "text", "value": "Play Online", "kind": "faded"}
        links.append(link)

        # View Files
        if self.actions["view"]:
            link = {"datum": "link", "value": "View Files", "url": self.view_url(), "roles": ["view-link"], "icons": self.get_major_icons()}
        else:
            link = {"datum": "text", "value": "View Files", "kind": "faded"}
        links.append(link)

        # Reviews
        if self.actions["review"]:
            link = {"datum": "link", "value": "Reviews ({})".format(self.review_count), "url": self.review_url(), "roles": ["review-link"]}
        else:
            link = {"datum": "text", "value": "Reviews (0)", "kind": "faded"}
        links.append(link)

        # Articles
        if self.actions["article"]:
            link = {"datum": "link", "value": "Articles ({})".format(self.article_count), "url": self.article_url(), "roles": ["article-link"]}
        else:
            link = {"datum": "text", "value": "Articles (0)", "kind": "faded"}
        links.append(link)

        # Attributes
        link = {"datum": "link", "value": "Attributes", "url": self.attributes_url(), "roles": ["attribute-link"]}
        links.append(link)

        if debug:
            link = {"datum": "link", "value": "Edit ZF#{}".format(self.id), "url": self.admin_url(), "roles": ["debug-link"], "kind": "debug"}
            links.append(link)
            link = {"datum": "link", "value": "Tools ZF#{}".format(self.id), "url": self.tool_url(), "roles": ["debug-link"], "kind": "debug"}
            links.append(link)

        return links

    def initial_context(self, *args, **kwargs):
        context = super(File, self).initial_context(*args, **kwargs)
        context["hash_id"] = self.filename
        context["file"] = self

        if hasattr(self, "extra_context"):
            context.update(self.extra_context)

        # Append roles/extras based on details
        if self.explicit:
            context["roles"].append("explicit")
        if self.is_detail(DETAIL_UPLOADED):
            context["roles"].append("unpublished")
        if self.is_detail(DETAIL_FEATURED):
            context["roles"].append("featured")
            context["extras"].append("museum_site/blocks/extra-featured-world.html")
            context["featured_articles"] = self.articles.category("Featured Game")
        if self.is_detail(DETAIL_LOST):
            context["roles"].append("lost")
            if self.description:
                context["extras"].append("museum_site/blocks/extra-lost.html")
                context["lost_description"] = self.description
        if self.is_detail(DETAIL_PROGRAM) and self.description:
            # TODO: This PK check is a hotfix for "description" being used for many types of descriptions
            if self.pk not in [85]:
                context["extras"].append("museum_site/blocks/extra-utility.html")
                context["utility_description"] = self.description
                context["detail_name"] = "Program"
        elif self.is_detail(DETAIL_UTILITY) and self.description:
            context["extras"].append("museum_site/blocks/extra-utility.html")
            context["utility_description"] = self.description
            context["detail_name"] = "Utility"

        return context

    def detailed_block_context(self, extras=None, *args, **kwargs):
        """ Return info to populate a detail block """
        context = self.initial_context(*args, **kwargs)
        context.update(
            tag={"opening": "div", "closing": "/div"},
            columns=[],
            title={"datum": "title", "value": self.title, "url": self.url(), "icons": self.get_all_icons()},
        )

        # Prepare Columns
        context["columns"].append([
            {"datum": "text", "label": "Author"+("s" if self.authors.count() > 1 else ""), "value": self.author_links()},
            {"datum": "text", "label": "Compan"+("ies" if self.companies.count() > 1 else "y"), "value": self.company_links()},
            {
                "datum": "link", "label": "Released", "value": (self.release_date or "Unknown"),
                "url": "/file/browse/year/{}/".format(self.release_year(default="unk"))
            },
            {"datum": "text", "label": "Genre"+("s" if self.genres.count() > 1 else ""), "value": self.genre_links()},
            {"datum": "text", "label": "Filename", "value": self.filename},
            {"datum": "text", "label": "Size", "value": filesizeformat(self.size)},
        ])

        context["columns"].append([
            {"datum": "text", "label": "Details", "value": self.details_links()},
            {
                "datum": "text", "label": "Rating",
                "value": self.rating_for_detailed_view(),
            },
            {
                "datum": "text", "label": "Boards", "value": self.boards_str(),
                "title": "Playable/Total Boards. Values are not 100% accurate." if self.total_boards else ""
            },
            {
                "datum": "text", "label": "Language"+("s" if len(self.ssv_list("language")) > 1 else ""),
                "value": self.language_links()
            },

        ])

        if self.is_detail(DETAIL_UPLOADED) and self.upload_set.first():
            context["columns"][1].append({"datum": "text", "label": "Upload Date", "value": self.upload_set.first().date})
        if not self.is_detail(DETAIL_UPLOADED) and self.publish_date:
            context["columns"][1].append({"datum": "text", "label": "Publish Date", "value": self.publish_date_str()})
        if self.is_detail(DETAIL_LOST):
            del context["title"]["url"]

        # Prepare Links
        context["links"] = self.links()

        if context["debug"]:
            context["columns"][1].append(
                {
                    "datum": "multi-link",
                    "roles": ["debug-link"],
                    "kind": "debug",
                    "label": "Debug",
                    "values": [
                        {"url": self.admin_url(), "text": "Edit {}".format(self.pk)},
                        {"url": self.tool_url(), "text": "Tools {}".format(self.pk)},
                    ]
                }
            )
        return context

    def file_viewer_block_context(self, extras=None, *args, **kwargs):
        context = self.detailed_block_context(*args, **kwargs)

        # Remove certain fields
        for c in context["columns"]:
            to_pop = []
            for x in range(0, len(c)):
                label = c[x].get("label", "")
                # Add a break to the rating
                if label.startswith("Rating"):
                    if self.review_count == 0:
                        c[x]["value"] = mark_safe(c[x]["value"].split(" (")[0])
                    else:
                        c[x]["value"] = mark_safe(c[x]["value"].replace(" (", "<br>("))
                if label.startswith("Filename") or label.startswith("Detail") or label.startswith("Publish Date") or label.startswith("Language"):
                    to_pop.insert(0, x)
            for i in to_pop:
                c.pop(i)

        return context

    def detailed_collection_block_context(self, extras=None, *args, **kwargs):
        # Additional modifications to display Files as part of a collection
        context = self.detailed_block_context(*args, **kwargs)
        context["collection_description"] = kwargs.get("collection_description")
        if context["collection_description"]:
            context["extras"].insert(0, "museum_site/blocks/extra-collection.html")
        return context

    def list_block_context(self, extras=None, *args, **kwargs):
        context = super(File, self).initial_context()
        context.update(self.initial_context(view="list"))

        # Prepare Links
        cells = []
        if self.actions is None:
            self.init_actions()

        if self.actions["download"]:
            link = {"datum": "link", "value": "DL", "url": self.download_url(), "tag": "td",
                    "icons": self.get_all_icons()}
        else:
            link = {"datum": "text", "value": "DL", "kind": "faded", "tag": "td"}
        cells.append(link)

        if self.actions["view"]:
            link = {"datum": "link", "value": self.title, "url": self.url(), "tag": "td",
                    "icons": self.get_all_icons()}
        else:
            link = {"datum": "text", "value": self.title, "tag": "td", "kind": "faded"}
        cells.append(link)

        cells.append({"datum": "text", "value": self.author_links(), "tag": "td"}),
        cells.append({"datum": "text", "value": self.company_links(), "tag": "td"}),
        cells.append({"datum": "text", "value": self.genre_links(), "tag": "td"}),
        cells.append(
            {"datum": "link", "value": (self.release_date or "Unknown"), "url": "/file/browse/year/{}/".format(self.release_year(default="unk")), "tag": "td"}
        )
        cells.append({"datum": "text", "value": self.rating_for_list_view(), "tag": "td"})

        # Modify download text if needed
        if self.downloads.count():
            cells[0]["value"] = "DLs…"
            cells[0]["url"] = "/download/{}".format(
                self.key
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
            title_datum = {"datum": "title", "value": self.title, "url": self.url(), "icons": self.get_all_icons()}
        else:
            title_datum = {"datum": "title", "value": self.title, "kind": "faded"}

        context.update(
            preview=dict(url=self.preview_url, alt=self.preview_url),
            title=title_datum,
            columns=[],
        )
        context["columns"].append([{"datum": "text", "value": self.author_links()}])
        return context

    def title_datum_context(self):
        # Returns a context for displaying the ZFile's title datum
        context = {"datum": "title", "tag": "h1", "value": self.title, "icons": self.get_all_icons()}
        return context

    def poll_block_context(self, extras=None, *args, **kwargs):
        context = self.gallery_block_context(*args, **kwargs)
        context["roles"].append(kwargs.get("bg"))
        context["extras"].insert(0, "museum_site/blocks/extra-poll-desc.html")
        if kwargs.get("option"):
            context["option"] = kwargs["option"]
        return context

    def _init_icons(self):
        # Populates major and minor icons for file
        self._minor_icons = []
        self._major_icons = []

        if self.explicit:
            self._major_icons.append(self.ICONS["explicit"])
        if self.is_detail(DETAIL_UPLOADED):
            self._major_icons.append(self.ICONS["unpublished"])
        if self.is_detail(DETAIL_LOST):
            self._major_icons.append(self.ICONS["lost"])
        if self.is_detail(DETAIL_WEAVE):
            self._major_icons.append(self.ICONS["weave"])
        if self.is_detail(DETAIL_FEATURED):
            self._minor_icons.append(self.ICONS["featured"])

    @mark_safe
    def rating_for_detailed_view(self):
        return self.rating_str() + " ({} Review{})".format(self.review_count, "s" if self.review_count != 1 else "")

    @mark_safe
    def rating_for_list_view(self):
        if self.review_count:
            output = "<span title='Review count'>R: {}</span><br><span title='Average Score'>S: {}</span>".format(
                self.review_count, self.rating_str(show_maximum=False)
            )
        else:
            output = "—"
        return output

    def remove_uploaded_zfile(self, upload):
        message = "Removing ZFile: "
        message += str(self) + "\n"

        # Remove the physical file
        path = self.phys_path()
        if os.path.isfile(path):
            os.remove(path)
            message += "Removed physical file\n"

        # Remove the Upload object
        if upload is not None:
            upload.delete()
            message += "Removed Upload object\n"
        else:
            message += "No Upload object detected.\n"

        # Remove the preview image
        screenshot_path = self.screenshot_phys_path()
        if screenshot_path:
            if os.path.isfile(screenshot_path):
                os.remove(screenshot_path)
                message += "Removed preview image\n"

        # Remove the contents objects
        content = self.content.all()
        for c in content:
            c.delete()
        message += "Remove Content object(s)\n"

        # Remove the file object
        self.delete()
        message += "Removed ZFile object\n"

        # Calculate queue size
        cache.set("UPLOAD_QUEUE_SIZE", File.objects.unpublished().count())
        message += "Updated cached queue size value. (Now: {})\n".format(cache.get("UPLOAD_QUEUE_SIZE"))
        return message

    def get_can_review_string(self):
        return File.REVIEW_LEVELS[self.can_review][1]

    def scan(self):
        issues = {}
        exists = True
        checksummed = True
        """ Used for Musuem Scan to identify basic issues """
        # Validate letter
        if self.letter not in "1abcdefghijklmnopqrstuvwxyz":
            issues["letter"] = "Invalid letter: '{}'".format(self.letter)
        if not os.path.isfile(self.phys_path()):
            issues["missing_file"] = "File not found: '{}'".format(self.phys_path())
            exists = False
        if not self.sort_title:
            issues["sort_title"] = "Sort title not set."
        if exists and self.size != os.path.getsize(self.phys_path()):
            issues["size_mismatch"] = "DB size doesn't match physical file size: {}/{}".format(self.size, os.path.getsize(self.phys_path()))
        if self.release_date and self.release_date.year < 1991:
            issues["release_date"] = "Release date is prior to 1991."
        if self.release_date and self.release_source == "":
            issues["release_date_source"] = "Release source is blank, but release date is set."
        if self.screenshot == "":
            issues["preview_image"] = "No preview image."
        if self.screenshot and (not os.path.isfile(os.path.join(STATIC_PATH, self.preview_url()))):
            issues["preview_image_missing"] = "Screenshot does not exist at {}".format(self.preview_url())

        # Review related
        reviews = Review.objects.for_zfile(self.id)
        rev_len = len(reviews)
        if rev_len != self.review_count:
            issues["review_count"] = "Reviews in DB do not match 'review_count': {}/{}".format(rev_len, self.review_count)

        # Detail related
        details = self.details.all()
        detail_list = []
        for detail in details:
            detail_list.append(detail.id)

        # Confirm LOST does not exist
        if DETAIL_LOST in detail_list and exists:
            issues["not_lost"] = "File is marked as 'Lost', but a Zip exists."

        articles = self.articles.all()
        article_len = len(articles)
        if article_len != self.article_count:
            issues["article_count"] = "Articles in DB do not match 'article_count': {}/{}".format(article_len, self.article_count)

        if not self.checksum:
            issues["blank_checksum"] = "Checksum not set."
            checksummed = False

        # Calculate file's checksum
        md5 = self.calculate_checksum(set_to_results=False)
        if checksummed and (self.checksum != md5):
            issues["checksum_mismatch"] = "Checksum in DB does not match calculated checksum: {} / {}".format(self.checksum, md5)

        # Board counts
        if (DETAIL_ZZT in detail_list) and self.playable_boards is None:
            issues["playable_boards"] = "File has no playable boards value but is marked as ZZT"

        if (DETAIL_ZZT in detail_list) and self.total_boards is None:
            issues["total_boards"] = "File has no total boards value but is marked as ZZT"

        if self.archive_name == "" and (DETAIL_LOST not in detail_list and DETAIL_UPLOADED not in detail_list):
            issues["archive_mirror"] = "File has no archive.org mirror"

        # Contents in DB vs Contents in zip
        db_contents = self.content.all()
        crcs = []
        for i in db_contents:
            crcs.append(i.crc32)

        zf = None
        try:
            zf = zipfile.ZipFile(self.phys_path())
        except (zipfile.BadZipFile, FileNotFoundError):
            zf = None

        if zf is not None:
            for zi in zf.infolist():
                if str(zi.CRC) not in crcs:
                    issues["content_error"] = "File's Contents object does not match ZipInfo"
                    break

        return issues

    def get_all_company_names(self):
        output = ""
        for company in self.companies.all():
            output += company.title + ", "
        output = output[:-2]
        return output

    def get_meta_tag_context(self):
        """ Returns a dict of keys and values for <meta> tags  """
        tags = {}
        tags["author"] = ["name", ", ".join(self.author_list())]
        tags["description"] = ["name", '"{}" by {}.'.format(self.title, ", ".join(self.author_list()))]
        if self.companies.count():
            tags["description"][1] += " Published by {}.".format(self.get_all_company_names())
        if self.release_date:
            tags["description"][1] += " ({})".format(self.release_date.year)

        tags["og:title"] = ["property", self.title + " - Museum of ZZT"]
        tags["og:image"] = ["property", self.preview_url()]  # Domain and static path to be added elsewhere
        return tags

    def author_unknown(self):
        """ Returns TRUE if the _only_ author is 'UNKNOWN' """
        return True if self.author_list() == ["Unknown"] else False

    def citation_str(self):
        """ Returns a string of standard information used in publication packs """
        title = '“{}”'.format(self.title)
        author = "by {}".format(", ".join(self.author_list())) if not self.author_unknown() else ""
        year = "({})".format(self.release_date.year) if self.release_date else ""
        return " ".join([title, author, year])


class ZFile_Admin(admin.ModelAdmin):
    exclude = ("content", "downloads",)

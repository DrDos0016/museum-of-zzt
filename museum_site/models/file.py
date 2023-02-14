import html
import os
import zipfile

from urllib.parse import quote

from django.core.cache import cache
from django.contrib import admin
from django.db import models
from django.template.defaultfilters import filesizeformat, escape
from django.utils.safestring import mark_safe

try:
    import zookeeper
    HAS_ZOOKEEPER = True
except ImportError:
    HAS_ZOOKEEPER = False

from museum_site.common import zipinfo_datetime_tuple_to_str
from museum_site.constants import SITE_ROOT, LANGUAGES, STATIC_PATH
from museum_site.core.detail_identifiers import *
from museum_site.core.file_utils import calculate_md5_checksum
from museum_site.core.misc import calculate_sort_title, get_letter_from_title, calculate_boards_in_zipfile
from museum_site.core.image_utils import optimize_image
from museum_site.core.transforms import qs_to_links
from museum_site.core.zeta_identifiers import *
from museum_site.models.zfile_legacy import ZFile_Legacy
from museum_site.models.zfile_urls import ZFile_Urls
from museum_site.models.review import Review
from museum_site.models.article import Article
from museum_site.models.base import BaseModel
from museum_site.querysets.zfile_querysets import *


class File(BaseModel, ZFile_Urls, ZFile_Legacy):
    """ ZFile object repesenting an a file hosted on the Museum site """
    model_name = "File"
    to_init = ["detail_ids", "icons", "actions", "extras"]
    table_fields = ["DL", "Title", "Author", "Company", "Genre", "Date", "Review"]
    cell_list = ["download", "view", "authors", "companies", "genres", "zfile_date", "rating"]
    guide_word_values = {"id": "pk", "title": "title", "author": "author", "company": "company", "rating": "rating", "release": "release_date", "publish_date": "publish_date", "uploaded": "upload_date"}

    # Uninitizalized shared attributes
    actions = None
    detail_ids = None
    extras = None
    all_downloads = None
    all_downloads_count = None

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

    SPECIAL_SCREENSHOTS = ["zzm_screenshot.png"]
    PREFIX_UNPUBLISHED = "UNPUBLISHED FILE - This file's contents have not been fully checked by staff."
    ICONS = {
        "explicit": {"glyph": "🔞", "title": "This file contains explicit content.", "role": "explicit-icon"},
        "unpublished": {"glyph": "🚧", "title": "This file is unpublished. Its contents have not been fully checked by staff.", "role": "unpub-icon"},
        "featured": {"glyph": "🗝️", "title": "This file is a featured world.", "role": "fg-icon"},
        "lost": {"glyph": "❌", "title": "This file is a known to be lost. Little if any data is available.", "role": "lost-icon"},
        "weave": {"glyph": "🧵", "title": "This file contains content designed for Weave ZZT.", "role": "weave-icon"},
    }

    (REVIEW_NO, REVIEW_APPROVAL, REVIEW_YES) = (0, 1, 2)
    REVIEW_LEVELS = (
        (REVIEW_NO, "Can't Review"),
        (REVIEW_APPROVAL, "Requires Approval"),
        (REVIEW_YES, "Can Review"),
    )

    # Database
    objects = ZFile_Queryset.as_manager()

    # Database Fields
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
    publish_date = models.DateTimeField(null=True, default=None, db_index=True, blank=True, help_text="Date File was published on the Museum")
    last_modified = models.DateTimeField(auto_now=True, help_text="Date DB entry was last modified")

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
    upload = models.ForeignKey("Upload", null=True, blank=True, on_delete=models.SET_NULL)
    zeta_config = models.ForeignKey("Zeta_Config", null=True, blank=True, default=1, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["sort_title", "letter"]

    def __str__(self):
        return "{} [{}][#{}]".format(self.title, self.key, self.id)

    # Initalizing functions
    def init_detail_ids(self):
        if self.detail_ids is None:
            self.detail_ids = self.details.all().values_list("id", flat=True)

    def _init_actions(self):
        """ Determine which actions may be performed on this zfile """
        self.actions = {"review": False}
        self.actions["download"] = True if self.downloads.all().count() else False
        self.actions["view"] = True if self.can_museum_download() else False
        self.actions["play"] = True if self.archive_name or (self.actions["view"] and self.supports_zeta_player()) else False
        self.actions["article"] = True if self.article_count else False
        # Review
        if (self.actions["download"] and self.can_review) or self.review_count:
            self.actions["review"] = True
        if self.actions["review"] and self.is_detail(DETAIL_UPLOADED):
            self.actions["review"] = False
        self.actions["attributes"] = True

    def _init_detail_ids(self):
        self.detail_ids = self.details.all().values_list("id", flat=True)

    def _init_extras(self):
        self.extras = []
        if DETAIL_FEATURED in self.detail_ids:
            self.extras.append({"kind": "featured-world", "template": "museum_site/subtemplate/extra-featured-world.html"})
        if DETAIL_LOST in self.detail_ids and self.description:
            self.extras.append({"kind": "lost-world", "template": "museum_site/subtemplate/extra-lost.html"})
        if DETAIL_PROGRAM in self.detail_ids and self.description:
            # TODO: This PK check is a hotfix for "description" being used for many types of descriptions
            if self.pk not in [85]:
                self.extras.append({"kind": "program-description", "template": "museum_site/subtemplate/extra-utility.html"})
        elif DETAIL_UTILITY in self.detail_ids and self.description:
            self.extras.append({"kind": "utility-description", "template": "museum_site/subtemplate/extra-utility.html"})

    def _init_roles(self, view):
        super()._init_roles(view)
        to_add = []

        if self.explicit:
            to_add.append("explicit")
        if DETAIL_UPLOADED in self.detail_ids:
            to_add.append("unpublished")
        if DETAIL_FEATURED in self.detail_ids:
            to_add.append("featured")
        if DETAIL_LOST in self.detail_ids:
            to_add.append("lost")

        for i in to_add:
            self.roles.append(i)

    def init_all_downloads(self):
        if self.all_downloads is None:
            self.all_downloads = self.downloads.all()
            self.all_downloads_count = len(self.all_downloads)

    # Database functions
    def basic_save(self, *args, **kwargs):
        super(File, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Pre save
        # Force lowercase letter
        if not self.letter:
            self.letter = get_letter_from_title(self.title)
        else:
            self.letter = self.letter.lower()

        self.sort_title = calculate_sort_title(self.title)  # Get sort title
        self.calculate_article_count()  # Recalculate Article Count

        # If the screenshot is blank and a file exists for it, set it
        file_exists = os.path.isfile(os.path.join(SITE_ROOT, "museum_site/static/images/screenshots/") + self.letter + "/" + self.filename[:-4] + ".png")
        if self.screenshot == "" and file_exists:
            self.screenshot = self.filename[:-4] + ".png"

        self.calculate_reviews()  # Calculate Review Scores

        # Update blank md5s
        if not self.checksum:
            self.checksum = calculate_md5_checksum(self.phys_path())

        # Set board counts for non-uploads
        if HAS_ZOOKEEPER and not kwargs.get("new_upload"):
            if not self.playable_boards or not self.total_boards:
                (self.playable_boards, self.total_boards) = calculate_boards_in_zipfile(self.phys_path())

        # Actual save call
        if kwargs.get("new_upload"):
            del kwargs["new_upload"]
        super(File, self).save(*args, **kwargs)

    # Filepaths
    def phys_path(self): return os.path.join(SITE_ROOT + self.download_url())

    def screenshot_phys_path(self):
        """ Returns the physical path to the preview image. If the file has no preview image set or is using a shared screenshot, return an empty string. """
        if self.screenshot and self.screenshot not in self.SPECIAL_SCREENSHOTS:
            return os.path.join(STATIC_PATH, "images/screenshots/{}/{}".format(self.letter, self.screenshot))
        else:
            return ""

    # Other Functions
    def file_exists(self): return True if os.path.isfile(self.phys_path()) else False

    def related_list(self, related):
        output = []
        for i in getattr(self, related).all():
            output.append(i.title)
        return output

    def author_list(self):
        """ STILL USED IN TEMPLATES """
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

    def is_detail(self, detail_id):
        self._init_detail_ids()  # TODO may or may not need to do this
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

    def calculate_size(self):
        self.size = os.path.getsize(self.phys_path())

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

        self.has_icons = True if len(self._minor_icons) or len(self._major_icons) else False

    def remove_uploaded_zfile(self):
        message = "Removing ZFile: "
        message += str(self) + "\n"

        # Remove the physical file
        path = self.phys_path()
        if os.path.isfile(path):
            os.remove(path)
            message += "Removed physical file\n"

        # Remove the Upload object
        if self.upload:
            self.upload.delete()
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
        message += "Removed Content object(s)\n"

        # Remove the download objects
        downloads = self.downloads.all()
        for d in downloads:
            d.delete()
        message += "Removed Download objects(s)\n"

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
        """ Used for Museum Scan to identify basic issues """
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
        md5 = calculate_md5_checksum(self.phys_path())
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
        tags["author"] = ["name", ", ".join(self.related_list("authors"))]
        tags["description"] = ["name", '"{}" by {}.'.format(self.title, ", ".join(self.related_list("authors")))]
        if self.companies.count():
            tags["description"][1] += " Published by {}.".format(self.get_all_company_names())
        if self.release_date:
            tags["description"][1] += " ({})".format(self.release_date.year)

        tags["og:title"] = ["property", self.title + " - Museum of ZZT"]
        tags["og:image"] = ["property", self.preview_url()]  # Domain and static path to be added elsewhere
        return tags

    def author_unknown(self):
        """ Returns TRUE if the _only_ author is 'UNKNOWN' """
        return True if self.related_list("authors") == ["Unknown"] else False

    def citation_str(self):
        """ Returns a string of standard information used in publication packs """
        title = '“{}”'.format(self.title)
        author = "by {}".format(", ".join(self.related_list("authors"))) if not self.author_unknown() else ""
        year = "({})".format(self.release_date.year) if self.release_date else ""
        return " ".join([title, author, year])

    def can_museum_download(self):
        """ Return TRUE if a zfiles Download object is associated with this file and the file exists """
        dl = self.downloads.filter(kind="zgames").first()
        if dl and dl.zgame_exists():
            return True
        return False

    # Fields for HTML display
    def get_field_download(self, view="detailed"):
        restricted = {"value": "<span class='faded'>{} <i>Download</i></span>".format(self.prepare_icons_for_field()), "safe": True}
        if not self.actions["download"]:
            if view == "list":
                restricted["value"] = restricted["value"].replace("Download", "DL")
            return restricted

        self.init_all_downloads()
        text = "Download" + ("s ({})".format(self.all_downloads_count) if self.all_downloads_count >= 2 else "")

        if self.all_downloads_count == 0:
            return restricted

        url = self.all_downloads.first().url if self.all_downloads_count == 1 else "/file/download/{}/".format(self.key)

        # Change text for list view
        if view == "list":
            text = "DLs…" if text.startswith("Downloads") else "DL"

        return {"label": "Download", "value": "<a href='{}'>{}{}</a>".format(url, self.prepare_icons_for_field(), text), "safe": True}

    def get_field_play(self, view="detailed"):
        if not self.actions["play"]:
            return {"value": "<span class='faded'>{} <i>Play Online</i></span>".format(self.prepare_icons_for_field("major")), "safe": True}
        url = "/file/play/{}/".format(self.key)
        return {"value": "<a href='{}'>{}{}</a>".format(url, self.prepare_icons_for_field("major"), "Play Online"), "safe": True}

    def get_field_view(self, view="detailed"):
        if view == "header":
            return {"value": "{}{}".format(self.prepare_icons_for_field(), self.title), "safe": True}
        if not self.actions["view"]:
            if view == "list" or view == "title":
                return {"value": "<span class='faded'>{} <i>{}</i></span>".format(self.prepare_icons_for_field(), escape(self.title)), "safe": True}
            return {"value": "<span class='faded'>{} <i>View Contents</i></span>".format(self.prepare_icons_for_field("major")), "safe": True}

        url = "/file/view/{}/".format(self.key) if self.can_museum_download() else ""
        texts = {"detailed": "View Contents"}
        text = escape(texts.get(view, self.title))
        icon_kind = "major" if view == "detailed" else "all"

        return {"value": "<a href='{}'>{}{}</a>".format(url, self.prepare_icons_for_field(icon_kind), text), "safe": True}

    def get_field_review(self, view="detailed"):
        restricted = {"value": "<span class='faded'><i>Reviews (0)</i></span>", "safe": True}  # If count is non-zero you can click the link
        if not self.actions["review"]:
            return restricted

        url = "/file/review/{}/".format(self.key)
        text = "Reviews ({})".format(self.review_count)
        return {"value": "<a href='{}'>{}</a>".format(url, text), "safe": True}

    def get_field_article(self, view="detailed"):
        restricted = {"value": "<span class='faded'><i>Articles (0)</i></span>", "safe": True}  # If count is non-zero you can click the link
        if not self.actions["article"]:
            return restricted
        url = "/file/article/{}/".format(self.key)
        text = "Articles ({})".format(self.article_count)
        return {"value": "<a href='{}'>{}</a>".format(url, text), "safe": True}

    def get_field_attributes(self, view="detailed"):
        restricted = {"value": "<span class='faded'><i>Articles (0)</i></span>", "safe": True}  # If count is non-zero you can click the link
        if not self.actions["attributes"]:
            return restricted
        url = "/file/attribute/{}/".format(self.key)
        return {"value": "<a href='{}'>Attributes</a>".format(url), "safe": True}

    def get_field_tools(self, view="detailed"):
        url = "/tools/{}/".format(self.key)
        return {"label": "Tools", "value": "<a href='{}'>Tools {} #{}</a>".format(url, self.model_name, self.pk), "safe": True}

    def get_field_authors(self, view="detailed"):
        qs = self.authors.all()
        plural = "s" if qs.count() > 1 else ""
        return {"label": "Author{}".format(plural), "value": qs_to_links(qs), "safe": True}

    def get_field_companies(self, view="detailed"):
        qs = self.companies.all()
        plural = "ies" if qs.count() > 1 else "y"
        return {"label": "Compan{}".format(plural), "value": qs_to_links(qs), "safe": True}

    def get_field_zfile_date(self, view="detailed"):
        if self.release_date is None:
            date_str = "<i>Unknown</i>"
            url = "/file/browse/year/{}/".format(self.release_year(default="unk"))
        else:
            date_str = self.release_date.strftime("%b %d, %Y")
            url = "/file/browse/year/{}/".format(self.release_year(default="unk"))

        return {"label": "Released", "value": "<a href='{}'>{}</a>".format(url, date_str), "safe": True}

    def get_field_genres(self, view="detailed"):
        qs = self.genres.all()
        plural = "s" if qs.count() > 1 else ""
        return {"label": "Genre{}".format(plural), "value": qs_to_links(qs), "safe": True}

    def get_field_filename(self, view="detailed"):
        return {"label": "Filename", "value": self.filename}

    def get_field_size(self, view="detailed"):
        return {"label": "Size", "value": filesizeformat(self.size), "title": "{} bytes".format(self.size)}

    def get_field_details(self, view="detailed"):
        qs = self.details.all()
        plural = "s" if qs.count() > 1 else ""
        return {"label": "Detail{}".format(plural), "value": qs_to_links(qs), "safe": True}

    def get_field_rating(self, view="detailed"):
        if self.rating is not None:
            long_rating = (str(self.rating) + "0")[:4]
            rating = "{} / 5.00".format(long_rating)
        else:
            rating = "<i>No rating</i>"

        plural = "s" if self.review_count != 1 else ""
        output = {"label": "Rating", "value": "{} ({} Review{})".format(rating, self.review_count, plural), "safe": True}
        if view == "list":
            if self.review_count:
                output = {"label": "Rating", "value": "{}<br>({})".format(rating.split(" ")[0], self.review_count), "safe": True}
            else:
                output = {"label": "Rating", "value": "{}".format(rating), "safe": True}
        if view == "header":
            output["value"] = output["value"].replace(" (", "<br>(")
        return output

    def get_field_boards(self, view="detailed"):
        return {
            "label": "Board Count", "value": "{} / {}".format(self.playable_boards, self.total_boards),
            "title": "Playable/Total boards. Values are automatic estimates and may be inaccurate."
        }

    def get_field_language(self, view="detailed"):
        language_str = ""
        for lang in self.language.split("/"):
            language_str += "<a href='/file/browse/language/{}/'>{}</a>, ".format(lang, LANGUAGES.get(lang, "Other"))
        return {"label": "Language", "value": language_str[:-2], "safe": True}

    def get_field_publish_date(self, view="detailed"):
        if (self.publish_date is None) or (self.publish_date.strftime("%Y-%m-%d") < "2018-11-07"):
            publish_date_str = "<i>Unknown</i>"
        else:
            publish_date_str = self.publish_date.strftime("%b %d, %Y, %I:%M:%S %p")

        return {"label": "Publish Date", "value": publish_date_str, "safe": True}

    def context_extras(self):
        # TODO This is probably the weakest part of this rewrite
        context = {}

        for extra in self.extras:
            kind = extra["kind"]
            if kind == "featured-world":
                context["featured_reviews"] = []
                # TODO: Eventually replace with articles.category() and show unpublished
                # articles = self.articles.category("Featured Game")
                articles = self.articles.filter(category="Featured Game").defer("content").order_by("-publish_date")
                for a in articles:
                    a.request = self.request
                    a._init_access_level()
                    a._init_icons()
                    context["featured_reviews"].append(a.get_field_view("title")["value"] + " by " + a.get_field_authors()["value"])
            elif kind == "lost-world":
                context["lost_description"] = self.description
            elif kind == "program-description":
                context["detail_name"] = "Program"
                context["utility_description"] = self.description
            elif kind == "utility-description":
                context["detail_name"] = "Utility"
                context["utility_description"] = self.description
        return context

    def process_kwargs(self, kwargs):
        if kwargs.get("poll_data"):  # Add poll data to display
            self.context["poll_description"] = kwargs["poll_data"].summary
            self.context["poll_patron_nominated"] = kwargs["poll_data"].backer
        if kwargs.get("zgames"):  # Include other Zgames to toggle between displaying information on
            self.context["zgames"] = kwargs["zgames"]
            self.context["other_zgame_count"] = len(self.context["zgames"]) - 1
        if kwargs.get("engine"):  # CL Info tags
            self.context["engine"] = kwargs["engine"]
            self.context["emulator"] = kwargs.get("emulator")
        return True

    # Context Methods
    def context_detailed(self):
        """ Context to display object as a detailed model block """
        context = self.context_universal()
        context["show_actions"] = True
        context["columns"] = []

        columns = [
            ["authors", "companies", "zfile_date", "genres", "filename", "size"],
            ["details", "rating", "boards", "language", "publish_date"],
        ]

        if self.show_staff:
            columns[1].append("edit")
            columns[1].append("tools")

        for col in columns:
            column_fields = []
            for field_name in col:
                field_context = self.get_field(field_name)
                column_fields.append(field_context)
            context["columns"].append(column_fields)

        action_list = ["download", "play", "view", "review", "article", "attributes"]
        if self.show_staff:
            action_list.append("edit")
            action_list.append("tools")
        actions = []
        for action in action_list:
            actions.append(self.get_field(action, view="detailed"))

        context["actions"] = actions
        return context

    def context_list(self):
        """ Context to display object as a list model block """
        context = self.context_universal()
        context["cells"] = []

        for field_name in self.cell_list:
            cell_fields = self.get_field(field_name, view="list")
            context["cells"].append(cell_fields)
        return context

    def context_gallery(self):
        """ Context to display object as a gallery model block """
        context = self.context_universal()
        context["fields"] = [
            self.get_field("authors", view="gallery")
        ]
        return context

    def context_poll(self):
        """ Context to display object as a poll model block (used when listed poll options) """
        context = self.context_gallery()
        context["roles"].append("gallery")
        return context

    def context_header(self):
        """ Context to display object as page header (such as in the file viewer) """
        context = self.context_universal()
        context["show_actions"] = True
        context["title"] = self.get_field_view(view="header")

        action_list = ["download", "play", "view", "review", "article", "attributes"]
        if self.show_staff:
            action_list.append("edit")
            action_list.append("tools")
        actions = []
        for action in action_list:
            actions.append(self.get_field(action, view="detailed"))

        context["actions"] = actions

        fields = ["authors", "companies", "zfile_date", "genres", "size", "rating", "boards"]
        context["fields"] = []
        for field_name in fields:
            field_context = self.get_field(field_name, "header")
            context["fields"].append(field_context)

        return context

    def context_cl_info(self):
        """ Context to display object for a Closer Look subject (cl_info templatetag) """
        context = self.context_universal()
        context["title"] = self.get_field_view(view="cl_info")
        context["engine"] = self.cl_info["engine"]
        context["emulator"] = self.cl_info["emulator"]

        fields = ["authors", "companies", "zfile_date"]
        context["fields"] = []
        for field_name in fields:
            field_context = self.get_field(field_name, "cl_info")
            context["fields"].append(field_context)

        action_list = ["download", "play"]
        actions = []
        for action in action_list:
            actions.append(self.get_field(action, view="cl_info"))
        actions.append(self.get_field_view(view="detailed"))
        context["actions"] = actions
        return context

    # Guide Word Functions
    def get_guideword_author(self):
        output = []
        for author in self.authors.all():
            output.append(author.title)
        return ", ".join(output)

    def get_guideword_company(self):
        output = []
        for author in self.companies.all():
            output.append(author.title)
        if output == []:
            return "<i>None</i>"
        return ", ".join(output)

    def get_guideword_rating(self): return self.rating_str()

    def get_guideword_release_date(self): return self.release_date.strftime("%b %d, %Y") if self.release_date is not None else "- Unknown Date -"
    def get_guideword_publish_date(self): return self.publish_date.strftime("%b %d, %Y") if self.publish_date is not None else "- Unknown Date -"
    def get_guideword_upload_date(self):
        if self.upload is not None:
            if self.upload.date:
                return self.upload.date.strftime("%b %d, %Y")
        return "- Unknown Date -"


class ZFile_Admin(admin.ModelAdmin):
    exclude = ("content", "downloads",)

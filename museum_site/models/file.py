import html
import os
import zipfile

from urllib.parse import quote

from django.core.cache import cache
from django.contrib import admin
from django.db import models
from django.template.defaultfilters import filesizeformat, escape
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

from museum_site.constants import SITE_ROOT, LANGUAGES, STATIC_PATH, DATE_NERD, DATE_FULL, DATE_HR
from museum_site.core.detail_identifiers import *
from museum_site.core.feedback_tag_identifiers import *
from museum_site.core.misc import calculate_sort_title, get_letter_from_title, calculate_boards_in_zipfile, zipinfo_datetime_tuple_to_str
from museum_site.core.image_utils import optimize_image
from museum_site.core.sorters import ZFile_Sorter
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
    to_init = ["icons"]
    table_fields = ["DL", "Title", "Author", "Company", "Genre", "Date", "Review"]
    cell_list = ["download", "view", "authors", "companies", "genres", "zfile_date", "rating"]
    guide_word_values = {
        "id": "pk", "title": "title", "author": "author", "company": "company", "rating": "rating", "release": "release_date",
        "publish_date": "publish_date", "uploaded": "upload_date"
    }

    sorter = ZFile_Sorter

    # Uninitizalized shared attributes
    all_downloads = None
    all_downloads_count = None

    ICONS = {
        "explicit": {"glyph": "🔞", "title": "This file contains explicit content.", "role": "explicit-icon"},
        "unpublished": {"glyph": "🚧", "title": "This file is unpublished. Its contents have not been fully checked by staff.", "role": "unpub-icon"},
        "featured": {"glyph": "🗝️", "title": "This file is a featured world.", "role": "fg-icon"},
        "lost": {"glyph": "❌", "title": "This file is known to be lost. Little if any data is available.", "role": "lost-icon"},
        "weave": {"glyph": "🧵", "title": "This file contains content designed for Weave ZZT.", "role": "weave-icon"},
        "antiquated": {"glyph": "⌛", "title": "This file is known to be antiquated. Its use is not recommended today.", "role": "outdated-icon"}
    }

    (FEEDBACK_NO, FEEDBACK_APPROVAL, FEEDBACK_YES) = (0, 1, 2)
    FEEDBACK_LEVELS = (
        (FEEDBACK_NO, "Can't Give Feedback"),
        (FEEDBACK_APPROVAL, "Requires Approval"),
        (FEEDBACK_YES, "Can Give Feedback"),
    )

    # Database
    objects = ZFile_Queryset.as_manager()

    # Database Fields
    letter = models.CharField(max_length=1, db_index=True, editable=False, help_text="Letter used for filtering browse pages")
    filename = models.CharField(max_length=50, help_text="Filename of the zip file containing this zfile's contents")
    key = models.CharField(
        unique=True, max_length=50, db_index=True, default="", help_text="Unique identifier used for URLs and filtering. Filename w/out extension"
    )
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
    file_license = models.CharField(max_length=150, default="Unknown", help_text="License the file is released under.")
    license_source = models.CharField(max_length=150, default="", blank=True, help_text="Source of licensing information.")

    # Derived Data
    checksum = models.CharField(max_length=32, blank=True, default="", help_text="md5 checksum of zip file")
    sort_title = models.CharField(
        max_length=100, db_index=True, default="", blank=True,
        help_text="Autogenerated value for actual title sorting. Strips articles and pads numbers to use leading digits."
    )

    # Reviews and Feedback
    review_count = models.IntegerField(
        default=0, editable=False, help_text="Cached count of review associated with this zip file. Set automatically. Do not adjust."
    )
    rating = models.FloatField(null=True, default=None, blank=True, help_text="Mean score based on all reviews with scores attached.")
    feedback_count = models.IntegerField(
        default=0, editable=False, help_text="Cached count of all feedback associated with this zip file. Set automatically. Do not adjust."
    )

    # Museum Properties
    explicit = models.BooleanField(default=False, help_text="Boolean to mark zfile as containing explicit content.")
    explicit_warning = models.CharField(max_length=1024, help_text="Specific warning for zfile's explicit content.", default="", blank=True)
    has_preview_image = models.BooleanField(default=False, help_text="Whether or not a preview image is available for this ZFile.")
    spotlight = models.BooleanField(default=True, help_text="Boolean to mark zfile as being suitable for display on the front page.")
    can_review = models.IntegerField(
        default=FEEDBACK_YES, choices=FEEDBACK_LEVELS, help_text="Choice of whether the file can be reviewed freely, pending approval, or not at all."
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
        ordering = ["sort_title"]

    def __str__(self):
        return "{} [{}][#{}]".format(self.title, self.key, self.id)

    def to_select(self):
        return "{} [{}]".format(self.title, self.key)

    # Cached Properties
    @cached_property
    def actions(self):
        output = {"download": False, "view": False, "play": False, "article": False, "review": False, "attributes": False}
        output["download"] = True if self.downloads.all().count() else False
        output["view"] = True if self.can_museum_download() else False
        output["play"] = True if self.archive_name or (output["view"] and self.supports_zeta_player()) else False
        output["article"] = True if self.article_count else False
        # Review
        if (output["download"] and self.can_review) or self.feedback_count:
            output["review"] = True
        output["attributes"] = True
        return output

    @cached_property
    def detail_ids(self):
        return self.details.all().values_list("id", flat=True)

    @cached_property
    def zgame(self):
        return self.downloads.filter(kind="zgames").first()

    @cached_property
    def extras(self):
        output = []
        if DETAIL_FEATURED in self.detail_ids:
            output.append({"kind": "featured-world", "template": "museum_site/subtemplate/extra-featured-world.html"})
        if DETAIL_LOST in self.detail_ids and self.description:
            output.append({"kind": "lost-world", "template": "museum_site/subtemplate/extra-lost.html"})
        if DETAIL_PROGRAM in self.detail_ids and self.description:
            # TODO: This PK check is a hotfix for "description" being used for many types of descriptions
            if self.pk not in [85]:
                output.append({"kind": "program-description", "template": "museum_site/subtemplate/extra-utility.html"})
        elif DETAIL_UTILITY in self.detail_ids and self.description:
            output.append({"kind": "utility-description", "template": "museum_site/subtemplate/extra-utility.html"})
        return output

    # Initalizing functions
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
    def save(self, *args, **kwargs):
        self.sort_title = calculate_sort_title(self.title)
        if self.pk:  # Updates for already saved models
            self.calculate_article_count()
        super(File, self).save(*args, **kwargs)

    # Filepaths
    def phys_path(self): return os.path.join(SITE_ROOT + self.download_url())

    def screenshot_phys_path(self):
        """ Returns the physical path to the preview image. If the file has no preview image set or is using a shared screenshot, return an empty string. """
        return os.path.join(STATIC_PATH, "screenshots/{}/{}.png".format(self.bucket(), self.key)) if self.has_preview_image else ""

    # Other Functions
    def bucket(self):
        bucket_name = str(self.pk // 1000 * 1000).zfill(4)
        return bucket_name

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

    def is_detail(self, detail_id):
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
            self.article_count = self.articles.accessible().count()

    def calculate_reviews(self):
        # Calculate Review Count
        if self.id is not None:
            self.review_count = Review.objects.for_zfile(self.id).filter(tags=FEEDBACK_TAG_REVIEW).count()

        # Calculate Rating
        if self.id is not None:
            ratings = Review.objects.average_rating_for_zfile(self.id)
            self.rating = None if ratings["rating__avg"] is None else round(ratings["rating__avg"], 2)

    def calculate_feedback(self):
        # Calculate Feedback Count
        if self.id is not None:
            self.feedback_count = Review.objects.for_zfile(self.id).count()

    def calculate_size(self):
        self.size = os.path.getsize(self.phys_path())

    def get_zip_info(self):
        try:
            zfh = zipfile.ZipFile(self.phys_path())
        except FileNotFoundError:
            return []
        return zfh.infolist()

    def release_year(self, default=""): return default if self.release_date is None else str(self.release_date)[:4]

    def language_pairs(self):
        language_list = self.language.split("/")
        output = []

        for i in language_list:
            output.append((LANGUAGES.get(i, i), i))
        return output

    def get_can_review_string(self):
        return File.FEEDBACK_LEVELS[self.can_review][1]

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

    def can_museum_download(self):
        """ Return TRUE if a zfiles Download object is associated with this file and the file exists """
        dl = self.downloads.filter(kind="zgames").first()
        if dl and dl.zgame_exists():
            return True
        return False

    # Fields for HTML display
    def get_field_download(self, view="detailed"):
        restricted = self.field_context(text="Download", icons="all", kind="faded")
        if not self.actions["download"]:
            if view == "list":
                restricted["value"] = restricted["value"].replace("Download", "DL")
            return restricted

        self.init_all_downloads()
        text = "Download" + ("s ({})".format(self.all_downloads_count) if self.all_downloads_count >= 2 else "")

        if self.all_downloads_count == 0:
            return restricted

        url = self.all_downloads.first().get_absolute_url() if self.all_downloads_count == 1 else reverse("zfile_download", kwargs={"key": self.key})

        # Change text for list view
        if view == "list":
            text = "DLs…" if text.startswith("Downloads") else "DL"

        return self.field_context(label="Download", url=url, icons="all", text=text)

    def get_field_play(self, view="detailed"):
        if not self.actions["play"]:
            return self.field_context(text="Play Online", icons="major", kind="faded")
        return self.field_context(url=reverse("zfile_play", kwargs={"key": self.key}), text="Play Online", icons="major")

    def get_field_view(self, view="detailed"):
        if view == "header":
            context = self.field_context(icons="all")
            context["value"] = self.title  # Text only, no link
            return context
        if not self.actions["view"]:
            if view == "list" or view == "title":
                return self.field_context(text=escape(self.title), icons="all", kind="faded")
            return self.field_context(text="View Contents", icons="all", kind="faded")

        url = reverse("file", kwargs={"key": self.key}) if self.can_museum_download() else ""
        texts = {"detailed": "View Contents"}
        text = escape(texts.get(view, self.title))
        icon_kind = "major" if view == "detailed" else "all"

        return self.field_context(url=url, icons=icon_kind, text=text)

    def get_field_review(self, view="detailed"):
        if not self.actions["review"]:
            return self.field_context(text="Feedback (0)", kind="faded")
        return self.field_context(url=reverse("zfile_review", kwargs={"key": self.key}), text="Feedback ({})".format(self.feedback_count))

    def get_field_article(self, view="detailed"):
        if not self.actions["article"]:
            return self.field_context(text="Articles (0)", kind="faded")
        return self.field_context(url=reverse("zfile_article", kwargs={"key": self.key}), text="Articles ({})".format(self.article_count))

    def get_field_attributes(self, view="detailed"):
        if not self.actions["attributes"]:
            return self.field_context(text="Attributes", kind="faded")
        return self.field_context(url=reverse("zfile_attribute", kwargs={"key": self.key}), text="Attributes")

    def get_field_tools(self, view="detailed"):
        return self.field_context(
            label="Tools", url=reverse("tool_index_with_file", kwargs={"key": self.key}), text="Tools {} #{}".format(self.model_name, self.pk)
        )

    def get_field_authors(self, view="detailed"):
        qs = self.authors.all()
        return self.field_context(label="Author{}".format("s" if qs.count() > 1 else ""), text=qs_to_links(qs), kind="text", clamped=True)

    def get_field_companies(self, view="detailed"):
        qs = self.companies.all()
        return self.field_context(label="Compan{}".format("ies" if qs.count() > 1 else "y"), text=qs_to_links(qs), kind="text", clamped=True)

    def get_field_zfile_date(self, view="detailed"):
        if self.release_date is None:
            date_str = "<i>Unknown</i>"
        else:
            date_str = self.release_date.strftime(DATE_HR)
        url = reverse("zfile_browse_field", kwargs={"field": "year", "value": self.release_year(default="unk")})
        return self.field_context(label="Released", text=date_str, url=url, kind="link")

    def get_field_genres(self, view="detailed"):
        qs = self.genres.all()
        return self.field_context(label="Genre{}".format("s" if qs.count() > 1 else ""), text=qs_to_links(qs), kind="link", clamped=True)

    def get_field_filename(self, view="detailed"):
        return self.field_context(label="Filename", text=self.filename, kind="text")

    def get_field_size(self, view="detailed"):
        return self.field_context(label="Size", text=filesizeformat(self.size), title="{} bytes".format(self.size), kind="text")

    def get_field_details(self, view="detailed"):
        qs = self.details.visible()
        return self.field_context(label="Detail{}".format("s" if qs.count() > 1 else ""), text=qs_to_links(qs), kind="text", clamped=True)

    def get_field_rating(self, view="detailed"):
        if self.rating is not None:
            long_rating = (str(self.rating) + "0")[:4]
            rating = "{} / 5.00".format(long_rating)
        else:
            rating = "<i>No rating</i>"

        plural = "s" if self.review_count != 1 else ""
        output = self.field_context(label="Rating", text="{} ({} Review{})".format(rating, self.review_count, plural), kind="text")
        if view == "list":
            if self.review_count:
                output = self.field_context(label="Rating", text="{}<br>({})".format(rating.split(" ")[0], self.review_count), kind="text")
            else:
                output = self.field_context(label="Rating", text="{}".format(rating), kind="text")
        if view == "header":
            output["value"] = output["value"].replace(" (", "<br>(")
        return output

    def get_field_boards(self, view="detailed"):
        return self.field_context(
            label="Board Count",
            text="{} / {}".format(self.playable_boards, self.total_boards),
            title="Playable/Total boards. Values are automatic estimates and may be inaccurate.",
            kind="text"
        )

    def get_field_language(self, view="detailed"):
        language_str = ""
        for lang in self.language.split("/"):
            url = reverse("zfile_browse_field", args=["language", LANGUAGES.get(lang, "other").lower()])
            language_str += "<a href='{}'>{}</a>, ".format(url, LANGUAGES.get(lang, "Other"))
        return self.field_context(label="Language", text=language_str[:-2], kind="text")

    def get_field_publish_date(self, view="detailed"):
        if (self.publish_date is None) or (self.publish_date.strftime(DATE_NERD) < "2018-11-07"):
            publish_date_str = "<i>Unknown</i>"
        else:
            publish_date_str = self.publish_date.strftime(DATE_FULL)
        return self.field_context(label="Publish Date", text=publish_date_str, kind="text")

    def get_field_upload_date(self, view="detailed"):
        if (self.upload is None or self.upload.date is None):
            upload_date_str = "<i>Unknown</i>"
        else:
            upload_date_str = self.upload.date.strftime(DATE_FULL)
        return self.field_context(label="Upload Date", text=upload_date_str, kind="text")

    def context_extras(self):
        # TODO This is probably the weakest part of this rewrite
        context = {}

        for extra in self.extras:
            kind = extra["kind"]
            if kind == "featured-world":
                context["featured_reviews"] = []
                articles = self.articles.category("Featured World").order_by("-publish_date")
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
            ["details", "rating", "boards", "language"],
        ]
        if self.is_detail(DETAIL_UPLOADED):
            columns[1].append("upload_date")
        else:
            columns[1].append("publish_date")

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
        context["title"] = self.get_field_view(view="cl_info") if (self.pk != -1) else {"value": "ERROR - ZFile Not Found"}
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

    @mark_safe
    def get_guideword_rating(self, show_maximum=False):
        if self.rating is not None:
            long_rating = (str(self.rating) + "0")[:4]
            if show_maximum:
                return "{} / 5.00".format(long_rating)
            return long_rating
        return "<i>No rating</i>"

    def get_guideword_release_date(self): return self.release_date.strftime(DATE_HR) if self.release_date is not None else "- Unknown Date -"
    def get_guideword_publish_date(self): return self.publish_date.strftime(DATE_HR) if self.publish_date is not None else "- Unknown Date -"

    def get_guideword_upload_date(self):
        if self.upload is not None:
            if self.upload.date:
                return self.upload.date.strftime(DATE_HR)
        return "- Unknown Date -"

    def get_engines(self):
        """ Engine for new file viewer to know determine rules for parsing """
        engines = []
        if self.is_detail(DETAIL_WEAVE):
            engines.append("WEAVE")
        elif self.is_detail(DETAIL_ZZT):
            engines.append("ZZT")
        elif self.is_detail(DETAIL_SZZT):
            engines.append("SZZT")
        return engines

    def get_all_attributes(self, include_staff_fields=False):
        output = {
            "board_count": {
                "playable": self.playable_boards,
                "total": self.total_boards,
            },
            "checksum": self.checksum,
            "explicit": self.explicit,
            "description": self.description,
            "filename": self.filename,
            "id": self.pk,
            "internet_archive_identifier": self.archive_name,
            "language": self.language,
            "last_modified": self.last_modified,
            "letter": self.letter,
            "publish_date": self.publish_date,
            "rating": self.rating,
            "release_date": self.release_date,
            "release_source": self.release_source,
            "has_preview_image": self.has_preview_image,
            "size": self.size,
            "supports_zeta": "TODO?",
            "title": self.title,
            "zeta_config": self.zeta_config,
            "permissions": {
            },
            "counts": {
                "alias_count": self.aliases.count(),
                "article_count": self.articles.count(),
                "author_count": self.authors.count(),
                "download_count": self.downloads.count(),
                "feedback_count": self.feedback_count,
                "genre_count": self.genres.count(),
                "review_count": self.review_count,
            },
            "upload_info": {
            },
            "aliases": {
            },
            "articles": {
            },
            "authors": list(
                self.authors.all().values_list("title", flat=True)
            ),
            "companies": list(
                self.companies.all().values_list("title", flat=True)
            ),
            "contents": {
            },
            "details": list(
                self.details.all().values_list("title", flat=True)
            ),
            "downloads": {
            },
            "feedback": {
            },
            "genres": list(
                self.genres.all().values_list("title", flat=True)
            )
        }

        if include_staff_fields:
            output["sort_title"] = self.sort_title
            output["license"] = self.file_license,
            output["license_source"] = self.license_source,
            output["can_spotlight"] = self.spotlight
        return output


class ZFile_Admin(admin.ModelAdmin):
    exclude = ("content", "downloads",)

import os

from bs4 import BeautifulSoup

from django.db import models
from django.template import Template, Context
from django.template.defaultfilters import slugify, linebreaks
from django.utils.safestring import mark_safe

from museum.settings import STATIC_URL
from museum_site.constants import *
from museum_site.core.misc import epoch_to_unknown
from museum_site.models.base import BaseModel
from museum_site.private import PASSWORD2DOLLARS, PASSWORD5DOLLARS
from museum_site.querysets.article_querysets import *


class Article(BaseModel):
    """ Article object repesenting an article """
    objects = Article_Queryset.as_manager()

    to_init = ["access_level", "icons"]
    model_name = "Article"
    table_fields = ["Title", "Author", "Date", "Category", "Description"]
    sort_options = [
        {"text": "Newest", "val": "-date"},
        {"text": "Oldest", "val": "date"},
        {"text": "Title", "val": "title"},
        {"text": "Author", "val": "author"},
        {"text": "Category", "val": "category"},
    ]
    sort_keys = {
        "-date": ["-publish_date", "title"],
        "date": ["publish_date", "title"],
        "title": ["title"],
        "author": ["author", "title"],
        "category": ["category", "title"],
        "id": ["id"],
        "-id": ["-id"],
    }

    SCHEMAS = (
        ("text", "Plaintext"),
        ("md", "Markdown"),  # TODO NOT WORKING 2022 (but also not used)
        ("html", "HTML"),
        ("django", "Django"),
        ("80col", "80 Column Text"),
    )

    (REMOVED, PUBLISHED, UPCOMING, UNPUBLISHED) = (0, 1, 2, 3)

    PUBLICATION_STATES = (
        (PUBLISHED, "Published"),
        (UPCOMING, "Upcoming"),
        (UNPUBLISHED, "Unpublished"),
        (REMOVED, "Removed"),
    )

    EARLY_ACCESS_PRICING = {UPCOMING: "$2.00 USD", UNPUBLISHED: "$5.00 USD"}

    user_access_level = PUBLISHED

    ICONS = {
        "upcoming": {"glyph": "🔒", "title": "This article is currently exclusive to $2+ Patrons.", "role": "upcoming-icon"},
        "unpublished": {"glyph": "🔒", "title": "This article is currently exclusive to $5+ Patrons", "role": "unpublished-icon"},
        "unlocked": {"glyph": "🔑", "title": "This non-public article may be read at your current patronage!", "role": "unlocked-icon"},
    }

    CATEGORY_CHOICES = (
        ("Bugs And Glitches", "Bugs And Glitches"),
        ("Closer Look", "Closer Look"),
        ("Contest", "Contest"),
        ("Featured Game", "Featured Game"),
        ("Help", "Help"),
        ("Historical", "Historical"),
        ("Interview", "Interview"),
        ("Let's Play", "Let's Play"),
        ("Livestream", "Livestream"),
        ("Postmortem", "Postmortem"),
        ("Publication Pack", "Publication Pack"),
        ("Walkthrough", "Walkthrough"),
        ("Misc", "Misc."),
    )

    # Fields
    title = models.CharField(help_text="Title of the the article.", max_length=100)
    author = models.CharField(help_text="Author(s) of the article. Slash separated.", max_length=50)
    category = models.CharField(help_text="Categorization of the article.", choices=CATEGORY_CHOICES, max_length=50)
    content = models.TextField(help_text="Body of the article.", default="")
    css = models.TextField(help_text="Custom CSS. Must include <style></style> if set.", default="", blank=True)
    schema = models.CharField(help_text="Schema for the article. Used to determine parsing method.", max_length=6, choices=SCHEMAS, default="django")
    publish_date = models.DateField(help_text="Date the article was made public on the Museum", default="1970-01-01")
    published = models.IntegerField(help_text="Publication Status", default=UNPUBLISHED, choices=PUBLICATION_STATES)
    last_modified = models.DateTimeField(help_text="Date DB entry was last modified", auto_now=True)
    last_revised = models.DateTimeField(help_text="Date article content was last revised", default=None, null=True, blank=True)
    revision_details = models.TextField(help_text="Reference for revisions made to the article", default="", blank=True)
    description = models.CharField(help_text="Blurb to summarize/pique interest in the article", max_length=250, default="", blank=True)
    allow_comments = models.BooleanField(help_text="Add a section for Disqus comments.", default=False)
    spotlight = models.BooleanField(help_text="Allow this article to be visible on the front page", default=True)
    static_directory = models.CharField(
        max_length=120,
        default="", blank=True,
        help_text=("Name of directory where static files for the article are stored:<br>/museum_site/static/articles/[year|unk]/[static_directory]")
    )
    secret = models.CharField(help_text=("Per-article key to allow non-patrons to read unpublished articles"), max_length=12, default="", blank=True)
    plug_patreon = models.BooleanField(help_text="Add a plug for the Patreon at the end of the article", default=True)

    # Associations
    series = models.ManyToManyField("Series", default=None, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        output = "[{}] {} by {}".format(self.id, self.title, self.author)
        return output

    def url(self):
        return "/article/view/{}/{}/".format(self.id, slugify(self.title))

    def preview_url(self):
        return os.path.join(self.path(), "preview.png")

    def path(self):
        year = self.publish_date.year if self.publish_date.year != 1970 else "unk"
        return ("articles/{}/{}/".format(year, self.static_directory))

    def render(self, context={}):
        """ Render article content for use in a django template """
        if self.schema == "django":
            context_data = {
                "TODO": "TODO", "CROP": "CROP",  # Expected TODO usage.
                "path": self.path,
                "request": context.get("request")
            }
            head = "{% load static %}\n{% load site_tags %}\n{% load zzt_tags %}"
            return Template(head + self.content).render(Context(context_data))
        elif self.schema == "html":
            return mark_safe(self.content)
        elif self.schema == "text":
            return linebreaks(mark_safe(self.content))
        elif self.schema == "80col":
            return '<pre class="80col cp437" id="80col-content">1{}</pre>'.format(self.content)

    @property
    def is_restricted(self):
        if self.published in [Article.UPCOMING, Article.UNPUBLISHED]:
            return True
        return False

    @property
    def published_string(self):
        """ Returns a human readable string for the article's publication state. """
        return Article.PUBLICATION_STATES[self.published - 1][1].lower()

    def series_links(self):
        """ Returns HTML links to related series """
        output = ""

        for s in self.series.all():
            output += '<a href="{}">{}</a>, '.format(s.url(), s.title)

        return output[:-2]

    def series_range(self):
        """ Returns a list of Articles with this article in the middle """
        output = []
        # TODO Better handling an article being in multiple series
        series = self.series.all().first()

        found_self = False
        remaining = 2
        for a in series.article_set.all().order_by("publish_date"):
            if remaining < 1:
                break
            if found_self:
                remaining -= 1

            output.append(a)

            if a.id == self.id:
                found_self = True

        return output[-5:]

    def get_series_links(self):
        output = []
        for s in self.series.only("id", "title"):
            output.append({"url": s.url, "text": s.title})
        return output

    def get_zfile_links(self):
        output = []
        for zf in self.file_set.all().order_by("sort_title"):
            output.append({"url": zf.url, "text": zf.title})
        return output

    @property
    def early_access_price(self):
        return self.EARLY_ACCESS_PRICING.get(self.published, "???")

    def initial_context(self, *args, **kwargs):
        context = super(Article, self).initial_context(*args, **kwargs)
        context["hash_id"] = "article-{}".format(self.pk)

        if hasattr(self, "extra_context"):
            context.update(self.extra_context)

            if self.extra_context.get("password_qs"):
                context["url"] = context["url"] + self.extra_context["password_qs"]

        return context

    def gallery_block_context(self, extras=None, *args, **kwargs):
        context = self.initial_context(*args, **kwargs)
        context.update(
            title={"datum": "title", "value": self.title, "url": self.url(), "icons": self.get_all_icons()},
            columns=[],
        )

        context["columns"].append([
            {"datum": "text", "value": self.author}
        ])

        if self.is_restricted:
            context["title"]["roles"] = ["restricted"]

        # Unlock articles for patrons
        context = self.unlock_check(context, view="gallery")

        return context

    def _init_icons(self, request={}, show_staff=False):
        # Populates major and minor icons for file
        self._minor_icons = []
        self._major_icons = []

        if self.published == self.UPCOMING:
            icon = self.ICONS["unlocked"] if self.user_access_level >= self.UPCOMING else self.ICONS["upcoming"]
            self._major_icons.append(icon)
        if self.published == self.UNPUBLISHED:
            icon = self.ICONS["unlocked"] if self.user_access_level >= self.UNPUBLISHED else self.ICONS["unpublished"]
            self._major_icons.append(icon)

        self.has_icons = True if len(self._minor_icons) or len(self._major_icons) else False

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

    def unlock_check(self, context, view="detailed"):
        """ Checks if a normally locked article should display as unlocked based on user profile or a POSTed password """
        patronage = 0
        secret = None
        if context["request"] and context["request"].user.is_authenticated:
            patronage = context["request"].user.profile.patronage
        if context["request"] and context["request"].POST.get("secret"):
            secret = context["request"].POST.get("secret")
            if secret == PASSWORD2DOLLARS:
                patronage = UPCOMING_ARTICLE_MINIMUM_PATRONAGE
            elif secret == PASSWORD5DOLLARS:
                patronage = UNPUBLISHED_ARTICLE_MINIMUM_PATRONAGE

        if view == "detailed" or view == "gallery":
            if self.published == self.UPCOMING and patronage >= UPCOMING_ARTICLE_MINIMUM_PATRONAGE:
                context["title"]["icons"] = [self.ICONS["unlocked"]]
                context["title"]["roles"].remove("restricted")
                context["title"]["roles"].append("unlocked")
                if secret:
                    context["title"]["url"] += "?secret={}".format(secret)
            if self.published == self.UNPUBLISHED and patronage >= UNPUBLISHED_ARTICLE_MINIMUM_PATRONAGE:
                context["title"]["icons"] = [self.ICONS["unlocked"]]
                context["title"]["roles"].remove("restricted")
                context["title"]["roles"].append("unlocked")
                if secret:
                    context["title"]["url"] += "?secret={}".format(secret)
        elif view == "list":
            if self.published == self.UPCOMING and patronage >= UPCOMING_ARTICLE_MINIMUM_PATRONAGE:
                context["cells"][0]["icons"] = [self.ICONS["unlocked"]]
                context["cells"][0]["roles"].remove("restricted")
                context["cells"][0]["roles"].append("unlocked")
            if self.published == self.UNPUBLISHED and patronage >= UNPUBLISHED_ARTICLE_MINIMUM_PATRONAGE:
                context["cells"][0]["icons"] = [self.ICONS["unlocked"]]
                context["cells"][0]["roles"].remove("restricted")
                context["cells"][0]["roles"].append("unlocked")

        return context

    def export_urls(self, domain=""):
        output = []

        raw = []
        if self.schema == "html" or self.schema == "django":
            soup = BeautifulSoup(self.content, "html.parser")

            for tag in soup.find_all("a"):
                raw.append(tag.get("href"))

        for r in raw:
            if r.startswith("{%"):
                tag = r.split(" ")
                if len(tag) > 4:
                    # print("HEY WEIRD TAG ALERT", self.id, self.title, tag)
                    output.append("!!SKIPME!! " + r)
            else:
                output.append(r)

        if domain:
            output = list(map(lambda o: domain + o if (not o.startswith("http") and not o.startswith("mailto")) else o, output))
        output.sort()

        return output

    def word_count(self):
        rendered = self.render()

        if self.schema == "html" or self.schema == "django":
            soup = BeautifulSoup(rendered, "html.parser")
            rendered = soup.get_text()

        words = rendered.replace("\r\n", " ").replace("\r", " ").replace("\n", " ").split(" ")
        count = 0
        for word in words:
            if word.strip() != "":
                count += 1

        return count

    def category_slug(self):
        return slugify(self.category)

    def get_meta_tag_context(self):
        """ Returns a dict of keys and values for <meta> tags  """
        tags = {}
        tags["author"] = ["name", self.author.replace("/", ", ")]
        tags["description"] = ["name", self.description]
        tags["og:title"] = ["property", self.title + " - Museum of ZZT"]
        tags["og:image"] = ["property", self.preview_url()]  # Domain and static path to be added elsewhere
        return tags

    def get_field_view(self, view="detailed"):
        url = "/article/view/{}/{}/".format(self.pk, slugify(self.title))
        texts = {"detailed": "View Contents", "list": self.title, "gallery": self.title, "title": self.title}
        text = texts[view]
        return {"value": "<a href='{}'>{}{}</a>".format(url, self.prepare_icons_for_field(), text), "safe": True}

    def get_field_authors(self, view="detailed"):
        authors = self.author.split("/")
        plural = "s" if len(authors) > 1 else ""
        return {"label": "Author{}".format(plural), "value": ", ".join(authors)}

    def get_field_article_date(self, view="detailed"):
        return {"label": "Publish Date", "value": self.publish_date}

    def get_field_category(self, view="detailed"):
        return {"label": "Category", "value": self.category}

    def get_field_series(self, view="detailed"):
        output = ""
        for s in self.series.all():
            output += '<a href="{}">{}</a>, '.format(s.url(), s.title)
        return {"label": "Series", "value": output[:-2], "safe": True}

    def get_field_description(self, view="detailed"):
        return {"label": "Description", "value": self.description}

    def get_field_associated_zfiles(self, view="detailed"):
        links = []
        for zf in self.file_set.all().order_by("sort_title"):
            zf._init_detail_ids()
            zf._init_icons()
            zf._init_actions()
            links.append(zf.get_field_view(view="title").get("value", ""))
        if links == []:
            link_str = "<i>None</i>"
        else:
            link_str = ", ".join(links)
        return {"label": "Associated Files", "value": link_str, "safe": True}


    def context_detailed(self):
        context = self.context_universal()
        context["roles"] = ["model-block", "detailed"]
        context["columns"] = []

        columns = [
            ["authors", "article_date", "category", "series", "associated_zfiles", "description"],
        ]
        fields = {}

        for col in columns:
            column_fields = []
            for field_name in col:
                field_context = self.get_field(field_name)
                if field_name == "series" and field_context.get("value", "") == "":
                    continue
                column_fields.append(field_context)
            context["columns"].append(column_fields)
        return context

    def context_list(self):
        context = self.context_universal()
        context["roles"] = ["list"]
        context["cells"] = []

        cell_list = ["view", "authors", "article_date", "category", "description"]
        for field_name in cell_list:
            cell_fields = self.get_field(field_name, view="list")
            context["cells"].append(cell_fields)
        return context

    def context_gallery(self):
        context = self.context_universal()
        context["roles"] = ["model-block", "gallery"]
        context["fields"] = [
            self.get_field("authors", view="gallery")
        ]
        return context

    def _init_access_level(self):
        if self.published == self.PUBLISHED:
            return True

        # Pull data from the request
        if self.request:
            patronage = self.request.user.profile.patronage if self.request.user.is_authenticated else 0
            secret = self.request.POST.get("secret", "")
            secret_get = self.request.GET.get("secret")
        else:
            patronage = 0
            secret = ""
            secret_get = None

        # Patronage based access level increases
        if patronage >= UNPUBLISHED_ARTICLE_MINIMUM_PATRONAGE:
            self.user_access_level = self.UNPUBLISHED
        elif patronage >= UPCOMING_ARTICLE_MINIMUM_PATRONAGE:
            self.user_access_level = self.UPCOMING

        # Password based access level increases
        self.user_access_level = self.UPCOMING if secret == PASSWORD2DOLLARS else self.user_access_level  # Universal Upcoming PW
        self.user_access_level = self.UNPUBLISHED if secret == PASSWORD5DOLLARS else self.user_access_level  # Universal Upcoming PW
        self.user_access_level = self.UNPUBLISHED if (secret_get == self.secret) else self.user_access_level  # Local PW

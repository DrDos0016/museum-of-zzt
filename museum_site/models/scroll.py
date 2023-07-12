from django.db import models
from django.template.defaultfilters import slugify

from museum_site.models.base import BaseModel
from museum_site.querysets.base import Base_Queryset


class Scroll(BaseModel):
    model_name = "Scroll"
    supported_views = ["list"]
    sort_options = [
        {"text": "Newest", "val": "-pk"},
        {"text": "Oldest", "val": "pk"},
        {"text": "Title", "val": "title"},
        {"text": "File", "val": "file"},
    ]
    sort_keys = {
        # Key - Value from <select> used in GET params
        # Value - Django order_by param
        "title": ["title"],
        "pk": ["pk"],
        "-pk": ["-pk"],
        "file": ["zfile__sort_title"],
        "id": ["id"],
        "-id": ["-id"],
    }
    guide_word_values = {"id": "pk", "title": "title", "file": "zfile"}
    table_fields = ["Title", "File", "Source"]
    cell_list = ["title", "zfile", "source"]

    # Database
    objects = Base_Queryset.as_manager()

    # Constants
    SCROLL_TOP = """```
╞╤═════════════════════════════════════════════╤╡
 │                  Scroll ###                 │
 ╞═════════════════════════════════════════════╡
 │    •    •    •    •    •    •    •    •    •│"""

    SCROLL_BOTTOM = """\n │    •    •    •    •    •    •    •    •    •│
╞╧═════════════════════════════════════════════╧╡```"""

    # Fields
    title = models.CharField(max_length=160)
    source = models.CharField(max_length=160)
    identifier = models.IntegerField(null=True, blank=True, default=None)
    content = models.TextField(
        default="",
        help_text="Lines starting with @ will be skipped. Initial whitespace is trimmed by DB, so an extra @ line is a fix."
    )
    published = models.BooleanField(default=False)
    suggestion = models.CharField(max_length=500, blank=True, default="")
    zfile = models.ForeignKey("File", on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return "Scroll #{} ID:{} Pub:{}".format(self.identifier, self.id, self.published)

    def url(self):
        return "/scroll/view/{}/{}/".format(self.id, slugify(self.title))

    def preview_url(self):
        return ""

    def admin_url(self):
        return "/admin/museum_site/scroll/{}/change/".format(self.id)

    def lines(self):
        return self.content.split("\n")

    def render_for_discord(self):
        lines = self.lines()

        output = self.SCROLL_TOP.replace("###", ("000"+str(self.identifier))[-3:])
        for line in lines:
            line = line.replace("\r", "")
            line = line.replace("\n", "")
            if line and line[0] == "@":
                continue
            output += "\n │  " + (line + " " * 42)[:42] + " │ "
        output += self.SCROLL_BOTTOM

        return output

    def content_as_text(self):
        raw = self.content
        lines = raw.split("\n")
        output = []
        for line in lines:
            if line.startswith("@"):
                continue
            output.append(line)
        return "\n".join(output)

    def save(self, *args, **kwargs):
        if self.published and not self.identifier:
            qs = Scroll.objects.filter(published=True).order_by("-identifier")
            s = qs.first()
            if s is None:
                self.identifier = 1
            else:
                self.identifier = s.identifier + 1

        if self.source.startswith("https://museumofzzt.com"):
            self.source = self.source.replace("https://museumofzzt.com", "")
        super().save(*args, **kwargs)

    def context_list(self):
        context = self.context_universal()
        context["cells"] = []

        for field_name in self.cell_list:
            cell_fields = self.get_field(field_name, view="list")
            context["cells"].append(cell_fields)
        return context

    def get_field_title(self, view="list"):
        return {"label": "", "value": "<a href='{}'>{}</a>".format(self.url(), self.title), "safe": True}

    def get_field_zfile(self, view="list"):
        return {"label": "", "value": "<a href='{}'>{}</a>".format(self.zfile.url(), self.zfile.title), "safe": True}

    def get_field_source(self, view="list"):
        return {"label": "", "value": "<a href='{}'>{}</a>".format(self.source, "Source"), "safe": True}

    def get_guideword_zfile(self):
        if self.zfile:
            return self.zfile.title
        else:
            return "- No file -"

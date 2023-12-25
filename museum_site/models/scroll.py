from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

from museum_site.core.sorters import Scroll_Sorter
from museum_site.models.base import BaseModel
from museum_site.querysets.base import Base_Queryset


class Scroll(BaseModel):
    model_name = "Scroll"
    supported_views = ["list"]
    guide_word_values = {"id": "pk", "title": "title", "file": "zfile"}
    sorter = Scroll_Sorter
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
        return "Scroll #{} ID:{} Pub:{}".format(self.pk, self.id, self.published)

    def get_absolute_url(self):
        return reverse("scroll_view", kwargs={"pk":self.pk, "slug":slugify(self.title)})

    def preview_url(self):
        return ""

    def lines(self):
        return self.content.split("\n")

    def render_for_discord(self):
        lines = self.lines()

        output = self.SCROLL_TOP.replace("###", ("000"+str(self.pk))[-3:])
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
        return {"label": "", "value": "<a href='{}'>{}</a>".format(self.get_absolute_url(), self.title), "safe": True}

    def get_field_zfile(self, view="list"):
        return {"label": "", "value": "<a href='{}'>{}</a>".format(self.zfile.get_absolute_url(), self.zfile.title), "safe": True}

    def get_field_source(self, view="list"):
        return {"label": "", "value": "<a href='{}'>{}</a>".format(self.source, "Source"), "safe": True}

    def get_guideword_zfile(self):
        if self.zfile:
            return self.zfile.title
        else:
            return "- No file -"

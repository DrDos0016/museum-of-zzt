from django.db import models


class Scroll(models.Model):
    model_name = "Scroll"
    # Constants
    SCROLL_TOP = """```
╞╤═════════════════════════════════════════════╤╡
 │                  Scroll ###                 │
 ╞═════════════════════════════════════════════╡
 │    •    •    •    •    •    •    •    •    •│"""

    SCROLL_BOTTOM = """\n │    •    •    •    •    •    •    •    •    •│
╞╧═════════════════════════════════════════════╧╡```"""

    # Fields
    identifier = models.IntegerField()
    content = models.TextField(
        default="",
        help_text="Lines starting with @ will be skipped. Initial whitespace is trimmed by DB, so an extra @ line is a fix."
    )
    source = models.CharField(max_length=160)
    published = models.BooleanField(default=False)
    suggestion = models.CharField(max_length=500, blank=True, default="")

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return "Scroll #{} ID:{} Pub:{}".format(self.identifier, self.id, self.published)

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
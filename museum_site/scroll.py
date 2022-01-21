from django.db import models


class Scroll(models.Model):
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
    content = models.TextField(default="")
    source = models.CharField(max_length=160)
    published = models.BooleanField(default=False)
    suggestion = models.CharField(max_length=500, blank=True, default="")

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return "Scroll #{} ID:{} Pub:{}".format(self.identifier, self.id, self.published)

    def lines(self):
        return self.content.split("\n")

    def render_for_discord(self):
        lines = self.lines()

        output = self.SCROLL_TOP.replace("###", ("000"+str(self.identifier))[-3:])
        for line in lines:
            line = line.replace("\r", "")
            line = line.replace("\n", "")
            output += "\n │  " + (line + " " * 42)[:42] + " │ "
        output += self.SCROLL_BOTTOM

        return output

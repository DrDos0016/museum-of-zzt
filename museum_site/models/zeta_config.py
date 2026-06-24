import json
import re
from django.db import models
from django.template.defaultfilters import escapejs

ZETA_CONFIG_CATEGORIES = (
    (0, "Recommended"),
    (1, "Alternative"),
    (2, "File Specific"),
    (3, "Hidden"),
)


class Zeta_Config_Manager(models.Manager):
    def select_list(self):
        # Only show generic options
        qs = self.filter(category__lte=1).order_by("category")
        output = []
        for zc in qs:
            output.append((zc.id, zc.name))
        output.append((-1, "Incompatible with Zeta"))
        return output


class Zeta_Config(models.Model):
    objects = Zeta_Config_Manager()

    # Constants
    model_name = "Zeta-Config"

    # Fields
    name = models.CharField(max_length=64)
    executable = models.CharField(max_length=128, default="zzt.zip", blank=True)
    arguments = models.CharField(max_length=128, default="", blank=True)
    commands = models.CharField(max_length=256, default="", blank=True)
    blink_duration = models.DecimalField(max_digits=6, decimal_places=3, default=0.466, help_text="0 = Force low colors. -1 = Enable high colors (aka NOBLINK)")
    charset = models.CharField(max_length=64, default="cp437")
    audio_buffer = models.IntegerField(default=2048)
    sample_rate = models.IntegerField(default=48000)
    note_delay = models.IntegerField(default=1)
    volume = models.DecimalField(default=0.2, max_digits=3, decimal_places=2)

    category = models.IntegerField(choices=ZETA_CONFIG_CATEGORIES)

    # Non-DB attributes
    client_config = False

    class Meta:
        ordering = ("category", "name")

    def __str__(self):
        return self.name

    def category_as_text(self):
        categories = ["Recommended", "Alternative", "File Specific", "Hidden"]
        return categories[int(self.category)]

    def get_required_substitutions(self):
        required_substitutions = []
        if "{SZZT_WORLD}" in self.arguments:
            required_substitutions.append("{SZZT_WORLD}")
        if "{FONT_FILE}" in self.commands:
            required_substitutions.append("{FONT_FILE}")
        if "{EXECUTABLE}" in self.commands:
            required_substitutions.append("{EXECUTABLE}")
        if "{32COMPAT}" in self.executable:
            required_substitutions.append("{32COMPAT}")
        return required_substitutions

    def user_configure(self, params):
        """ Modify configuration based on request.GET values """
        self.client_config = True
        if params.get("zeta_config"):  # This is for display purposes
            self.id = int(params["zeta_config"])
        if params.get("blink_cycle"):
            self.blink_duration = float(params["blink_cycle"])
        if params.get("charset_override"):
            self.charset = params["charset_override"]
        if params.get("no_args"):
            self.arguments = ""
        if params.get("no_commands"):
            self.commands = ""
        if params.get("bufferSize"):
            self.audio_buffer = int(params["bufferSize"])
        if params.get("sampleRate"):
            self.sample_rate = int(params["sampleRate"])
        if params.get("noteDelay"):
            self.note_delay = int(params["noteDelay"])
        if params.get("volume"):
            self.volume = float(params["volume"])
        if params.get("executable") and params["executable"] != "AUTO":
            self.executable = params["executable"]
        if self.executable == "NONE":
            self.executable = None

    def apply_configuration(self, settings, replacements={}):
        print("APPLYING", self.name, self.arguments)
        #[{"type": "zip", "url": "/static/data/zeta86_engines/zzt.zip"}]
        if self.executable:
            settings["files"] = [{"type": "zip", "url": "/static/data/zeta86_engines/{}".format(self.executable)}]  + settings["files"]
        if self.arguments:
            settings["arg"] = self.arguments
        if self.commands:
            settings["commands"] = self.commands
        if self.blink_duration:
            None
        return settings

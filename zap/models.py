import json

from django.db import models
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class Event(models.Model):

    # Fields
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=100)
    kind = models.CharField(max_length=80)
    json_str = models.TextField()
    image_render_datetime = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return self.title

    def get_json_data(self):
        return json.loads(self.json_str)

    def get_image_render_url(self):
        return "/static/zap/renders/event-{}-image-render.png".format(self.pk)

    @mark_safe
    def render(self):
        context = self.get_json_data()
        return render_to_string("zap/subtemplate/{}.html".format(self.kind), context).strip()

    def prefab_post(self):
        """ Calls dedicated prefab post function based on kind of event """
        return getattr(self, "prefab_post_" + self.kind.replace("-", "_"))()

    def prefab_post_stream_schedule(self):
        context = self.get_json_data()
        output = (
            "Stream Schedule [{} - {}]\n"
            "Watch Live: https://twitch.tv/worldsofzzt\n"
            "View Schedule: https://museumofzzt.com/event/view/{}/\n"
        ).format(context["date_start"], context["date_end"], self.pk)

        if context.get("title_1"):
            output += "{} @ {} -  {}\n".format(context["date_1"], context["time_1"], context["title_1"])
        if context.get("title_2"):
            output += "{} @ {} -  {}\n".format(context["date_2"], context["time_2"], context["title_2"])
        if context.get("title_3"):
            output += "{} @ {} -  {}\n".format(context["date_3"], context["time_3"], context["title_3"])
        return output.strip()

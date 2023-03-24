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



class Post(models.Model):
    # Fields
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    body = models.TextField()
    media_1 = models.CharField(max_length=255, blank=True, default="")
    media_2 = models.CharField(max_length=255, blank=True, default="")
    media_3 = models.CharField(max_length=255, blank=True, default="")
    media_4 = models.CharField(max_length=255, blank=True, default="")

    tweet_id = models.CharField(default="", blank=True, max_length=32)
    tumblr_id = models.CharField(default="", blank=True, max_length=32)
    mastodon_id = models.CharField(default="", blank=True, max_length=32)
    patreon_id = models.CharField(default="", blank=True, max_length=32)
    cohost_id = models.CharField(default="", blank=True, max_length=32)

    event = models.ForeignKey("Event", null=True, blank=True, on_delete=models.SET_NULL)

    def posted_where(self):
        where = []
        if self.tweet_id:
            where.append("twitter")
        if self.tumblr_id:
            where.append("tumblr")
        if self.mastodon_id:
            where.append("mastodon")
        if self.patreon_id:
            where.append("patreon")
        if self.cohost_id:
            where.append("cohost")
        return where

    def get_social_id_dict(self):
        output = {}
        if self.tweet_id:
            output["twitter"] = self.tweet_id
        if self.tumblr_id:
            output["tumblr"] = self.tumblr_id
        if self.mastodon_id:
            output["mastodon"] = self.mastodon_id
        if self.patreon_id:
            output["patreon"] = self.patreon_id
        if self.cohost_id:
            output["cohost"] = self.cohost_id
        return output

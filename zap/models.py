import json

from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe


class Post(models.Model):
    # Fields
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=80, default="Untitled")

    body = models.TextField()
    media_1 = models.CharField(max_length=255, blank=True, default="")
    media_2 = models.CharField(max_length=255, blank=True, default="")
    media_3 = models.CharField(max_length=255, blank=True, default="")
    media_4 = models.CharField(max_length=255, blank=True, default="")

    tweet_id = models.CharField(default="", blank=True, max_length=32)
    tumblr_id = models.CharField(default="", blank=True, max_length=32)
    mastodon_id = models.CharField(default="", blank=True, max_length=32)
    patreon_id = models.CharField(default="", blank=True, max_length=32)
    bluesky_id = models.CharField(default="", blank=True, max_length=255)

    def __str__(self):
        return "{} - {}".format(self.modified, self.title)

    def posted_where(self):
        where = []
        if self.tweet_id and self.tweet_id != "0":
            where.append("twitter")
        if self.tumblr_id and self.tumblr_id != "0":
            where.append("tumblr")
        if self.mastodon_id and self.mastodon_id != "0":
            where.append("mastodon")
        if self.patreon_id and self.mastodon_id != "0":
            where.append("patreon")
        if self.bluesky_id and self.bluesky_id != "0":
            where.append("bluesky")
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
        if self.patreon_id:
            output["bluesky"] = self.bluesky_id
        return output

    def posted_where_links(self):
        output = []
        where = self.posted_where()

        service_urls = {
            "twitter": "https://twitter.com/worldofzzt/status/{}".format(self.tweet_id),
            "tumblr": "https://worldsofzzt.tumblr.com/post/{}".format(self.tumblr_id),
            "mastodon": "https://botsin.space/@worldsofzzt/{}".format(self.mastodon_id),
            "bluesky": "https://bsky.app/profile/worldsofzzt.bsky.social/post/{}".format(self.bluesky_id.split(";")[0].split("/")[-1])
        }

        for service in where:
            html = '<a href="{}" target="_blank" class="noext"><img src="/static/zap/icons/{}.png".></a>'.format(service_urls[service], service)
            output.append(html)
        return output

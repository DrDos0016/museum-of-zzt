import json
import os
import time

from museum_site.constants import APP_ROOT, HOST, APP_ROOT

import pytumblr
import requests

from mastodon import Mastodon
from twitter import *
from atproto import Client, models, client_utils

from museum_site.settings import (
    BLUESKY_USER,
    BLUESKY_PASSWORD,

    MASTODON_CLIENT_KEY,
    MASTODON_CLIENT_SECRET,
    MASTODON_ACCESS_TOKEN,
    MASTODON_EMAIL,
    MASTODON_PASS,
    MASTODON_SECRETS_FILE,

    TUMBLR_OAUTH_CONSUMER,
    TUMBLR_OAUTH_CONSUMER_SECRET,
    TUMBLR_OAUTH_TOKEN,
    TUMBLR_OAUTH_SECRET,

    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    TWITTER_OAUTH_TOKEN,
    TWITTER_OAUTH_SECRET,

    DISCORD_WEBHOOK_ANNOUNCEMENTS_URL, DISCORD_WEBHOOK_PATRONS_URL, DISCORD_WEBHOOK_TEST_URL, DISCORD_WEBHOOK_FEED_URL,
)


class Social():
    """ Base Class - Do not use directly """
    reply_to = None
    response_history = []
    media = []
    uploaded_media = []

    def __init__(self):
        self._init_keys()
        self.login()

    def log_response(self, response):
        self.response_history.append(response)

    def get_last_response(self):
        return self.response_history[-1]

    def reset(self, clear_history=True):
        self.reply_to = None
        self.media = []
        self.uploaded_media = []
        if clear_history:
            self.response_history = []

    def reset_media(self):
        self.media = []
        self.uploaded_media = []

    def clean_hashtags(self, tags):
        # IN: "#zzt, #stream schedule, #darkdigital" | OUT: " #zzt #stream_schedule #darkdigital"
        post_tags = ""
        if tags:
            tags = tag.split(", ")
            for tag in tags:
                tag = tag.replace(" ", "_")
                post_tags += " " + tag
        return post_tags


class Social_Bluesky(Social):
    # https://github.com/MarshalX/atproto/blob/main/packages/atproto_client/client/client.py
    def _init_keys(self):
        self.user = BLUESKY_USER
        self.password = BLUESKY_PASSWORD

    def login(self):
        self.client = Client()
        response = self.client.login(self.user, self.password)
        self.log_response(response)
        return response

    def upload_media(self, media_path=None, media_url=None, media_bytes=None):
        if media_bytes:
            print("Bytes are currently unsupported.")
            return False
        if media_url:
            print("External media is currently unsupported.")
            return False
        if media_path:
            print("MEDIA PATH IS", media_path)
            self.media.append(media_path)

    def post(self, body, title="", tags="", reply_to=None):
        text_builder = client_utils.TextBuilder()

        # Break up linebreaks and spaces
        lines = body.split("\n")

        for line in lines:
            first_in_line = True
            words = line.split(" ")
            for word in words:
                if not first_in_line:
                    text_builder.text(" ")
                if word.startswith("http"):
                    text_builder.link(word, word.strip()) # URLs cannot contain \r\n and such
                else:
                    text_builder.text(word)
                first_in_line = False
            if not first_in_line:
                text_builder.text("\n")

        # Add hashtags
        if tags:
            hashtag_list = self.clean_hashtags(tags)
            for tag in hashtag_list:
                text_builder.text(" ")
                text_builder.tag("#" + tag, tag)

        # Add media
        images = []
        if self.media:
            for m in self.media:
                with open(m, "rb") as fh:
                    images.append(fh.read())
            response = self.client.send_images(text=text_builder, images=images, reply_to=reply_to)  # TODO alt text would go here
        else:
            response = self.client.send_post(text_builder, reply_to=reply_to)

        self.media = []
        self.log_response(response)
        return response

    def clean_hashtags(self, tags):
        # Hashtag string to array
        # IN: "#zzt, #museum of zzt, #ascii" OUT: ["zzt" , "museum of zzt", "ascii"]
        hashtag_list = []
        raw_tags = tags
        tags = raw_tags.split(",")
        for tag in tags:
            tag = tag.strip().replace(" ", "_")
            if tag.startswith("#"):
                hashtag_list.append(tag[1:])
        return hashtag_list

    def wozzt_reply(self, response, reply_body):
        root_post_ref = models.create_strong_ref(response)
        reply_resp = self.post(body=reply_body, reply_to=models.AppBskyFeedPost.ReplyRef(parent=root_post_ref, root=root_post_ref))
        return reply_resp


class Social_Discord(Social):
    channel_key = "test"
    mentions = []

    def _init_keys(self):
        # No keys to initialize
        return True

    def login(self):
        # No login required
        return True

    def upload_media(self, media_path=None, media_url=None, media_bytes=None):
        # TODO
        return True

    def post(self, body, title="", tags=""):
        destinations = {
            "announcements": DISCORD_WEBHOOK_ANNOUNCEMENTS_URL, "patrons": DISCORD_WEBHOOK_PATRONS_URL, "moz-feed": DISCORD_WEBHOOK_FEED_URL,
            "test": DISCORD_WEBHOOK_TEST_URL, "log": DISCORD_WEBHOOK_TEST_URL,
        }
        destination_webhook = destinations.get(self.channel_key)

        if self.mentions:
            mentions = " ".join(map(lambda foo: "<@&{}>".format(foo), self.mentions))
            body = mentions + " " + body

        discord_data = {"content": body}

        """
        if self.cleaned_data["image_embeds"]:
            embeds = []
            for embed in self.cleaned_data["image_embeds"]:
                embeds.append({"image": {"url": embed}})
            discord_data["embeds"] = embeds
        """

        response = requests.post(destination_webhook, headers={"Content-Type": "application/json"}, data=json.dumps(discord_data))
        self.log_response(response)
        return response

    def set_channel_key(self, key):
        self.channel_key = key

    def set_mentions(self, roles):
        self.mentions = roles


class Social_Mastodon(Social):
    def _init_keys(self):
        self.consumer_key = MASTODON_CLIENT_KEY
        self.consumer_secret = MASTODON_CLIENT_SECRET
        self.token = MASTODON_ACCESS_TOKEN
        self.email = MASTODON_EMAIL
        self.password = MASTODON_PASS

    def login(self):
        self.client = Mastodon(client_id=MASTODON_SECRETS_FILE)
        response = self.client.log_in(MASTODON_EMAIL, MASTODON_PASS)

        self.log_response(response)
        return response

    def upload_media(self, media_path=None, media_url=None, media_bytes=None):
        if media_bytes:
            print("Bytes are currently unsupported.")
            return False
        if media_url:
            print("External media is currently unsupported.")
            return False
        if media_path:
            response = self.client.media_post(media_file=media_path)

        if response.get("url"):
            self.media.append(response)

        self.log_response(response)
        return response

    def post(self, body, title="", tags=""):
        if tags:
            body += self.clean_hashtags(tags)

        if self.media:
            media = []
            for m in self.media:
                media.append(m["id"])
        else:
            media = None
        response = self.client.status_post(status=body, in_reply_to_id=self.reply_to, media_ids=media)

        self.uploaded_media = []
        self.log_response(response)
        return response

    def boost(self, post_id):
        response = self.client.status_reblog(str(post_id))
        self.log_response(response)
        return response


class Social_Tumblr(Social):
    def _init_keys(self):
        self.consumer_key = TUMBLR_OAUTH_CONSUMER
        self.consumer_secret = TUMBLR_OAUTH_CONSUMER_SECRET
        self.token = TUMBLR_OAUTH_TOKEN
        self.oauth_secret = TUMBLR_OAUTH_SECRET

    def login(self):
        self.client = pytumblr.TumblrRestClient(self.consumer_key, self.consumer_secret, self.token, self.oauth_secret)

    def upload_media(self, media_path=None, media_url=None, media_bytes=None):
        print("Uploading media")
        if media_bytes:
            print("Bytes are currently unsupported.")
            return False
        if media_url:
            path("External media is currently unsupported.")
            return False
        if media_path:
            self.uploaded_media.append(os.path.join(APP_ROOT, media_path))
        return True

    def post(self, body, title="", tags=""):
        if tags:  # tumblr wants hashtags as an array in the form of ["food", "pizza", "cooking"]
            tags = self.clean_hashtags(tags)

        if self.uploaded_media:
            if "http" in body:
                body = body.replace("\r", " ")
                body = body.replace("\n", " ")
                pre = body[body.find("http"):]
                url = pre[:pre.find(" ")].strip()
                response = self.client.create_link("worldsofzzt", state="published", tags=tags, url=url, description=body, title=title)
                # this can take a thumbnail URL with a thumbnail kwarg, but doesn't work with the uploaded media
            else:
                response = self.client.create_photo("worldsofzzt", state="published", tags=tags, caption=body, data=self.uploaded_media)
        else:
            if "http" in body:
                body = body.replace("\r", " ")
                body = body.replace("\n", " ")
                pre = body[body.find("http"):]
                url = pre[:pre.find(" ")].strip()
                response = self.client.create_link("worldsofzzt", state="published", tags=tags, url=url, description=body, title=title)
            else:
                response = self.client.create_text("worldsofzzt", state="published", tags=tags, body=body, title=title)

        self.uploaded_media = []
        self.log_response(response)
        return response

    def clean_hashtags(self, tags):
        # Hashtag string to array
        # IN: "#zzt, #museum of zzt, #ascii" OUT: ["zzt" , "museum of zzt", "ascii"]
        hashtag_list = []
        raw_tags = tags
        tags = raw_tags.split(",")
        for tag in tags:
            tag = tag.strip()
            if tag.startswith("#"):
                hashtag_list.append(tag[1:])
        return hashtag_list

    def boost(self, post_id):
        response = self.client.posts("worldsofzzt", type=None, **{"id": post_id})
        self.log_response(response)

        if response.get("posts") and response["posts"][0].get("reblog_key"):
            reblog_key = response["posts"][0]["reblog_key"]

            response = self.client.reblog("worldsofzzt", id=post_id, reblog_key=reblog_key)
            self.log_response(response)

        return response


class Social_Twitter(Social):
    def _init_keys(self):
        self.consumer_key = TWITTER_CONSUMER_KEY
        self.consumer_secret = TWITTER_CONSUMER_SECRET
        self.token = TWITTER_OAUTH_TOKEN
        self.oauth_secret = TWITTER_OAUTH_SECRET

    def login(self):
        auth = OAuth(self.token, self.oauth_secret, self.consumer_key, self.consumer_secret)
        self.client = Twitter2(auth=auth)
        self.upload_client = Twitter(domain='upload.twitter.com', auth=auth)

    def upload_media(self, media_path=None, media_url=None, media_bytes=None):
        if media_bytes:
            print("Bytes are currently unsupported.")
            return False
        if media_url:
            print("External media is currently unsupported.")
            return False
        if media_path:
            with open(media_path, "rb") as imagefile:
                imagedata = imagefile.read()

                response = self.upload_client.media.upload(media=imagedata)["media_id_string"]

                if response:
                    self.media.append(response)

                self.log_response(response)
        return response

    def post(self, body, title="", tags=""):
        if tags:
            body += self.clean_hashtags(tags)

        json_data = {"text": body}
        if self.media:
            json_data["media"] = {
                "media_ids": self.media
            }

        response = self.client.tweets(_json=json_data)

        self.uploaded_media = []
        self.log_response(response)
        return response

    def boost(self, post_id):
        """ IDK if this is possible on the free tier
        print("Post ID", post_id)
        post_id = str(post_id)
        # Must un-retweet to prevent errors for re-retweet attempts
        #response = self.client.statuses.unretweet(id=post_id)
        #response = self.client.tweets(_json={"id": "4800564439", "source_tweet_id": post_id})  # TODO Unhardcode @WoZZT User ID
        #self.log_response(response)
        #time.sleep(0.5)  # Probably not necessary
        #response = self.client.statuses.retweet(id=post_id)
        json_data = {
            "tweet_id": post_id
        }
        response = self.client.users._id.retweets(_id="4800564439", _json=json_data) # TODO Unhardcode @WoZZT User ID (_id param)
        self.log_response(response)
        return response
        """
        return {"reminder": "Twitter Boosting is unavailable."}

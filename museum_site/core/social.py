import json
import os
import time

from museum_site.constants import APP_ROOT, HOST, APP_ROOT, SITE_ROOT

import pytumblr
import requests
import tweepy

from mastodon import Mastodon
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

    TWITTER_BEARER_TOKEN,
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
            tags = tags.split(", ")
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
        if media_bytes:
            print("Bytes are currently unsupported.")
            return False
        if media_url:
            print("External media is currently unsupported.")
            return False
        if media_path:
            print("MEDIA PATH IS", media_path)
            self.media.append(media_path)

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

        # Add media
        images = []
        if self.media:
            for m in self.media:
                if m.startswith(SITE_ROOT):  # This is from the ZAP form
                    m = m.replace(SITE_ROOT, "").replace("/museum_site/", "")
                images.append("https://museumofzzt.com/" + m)
        if images:
            discord_data["embeds"] = []
            for i in images:
                discord_data["embeds"].append({"image": {"url": i}})

        response = requests.post(destination_webhook, headers={"Content-Type": "application/json"}, data=json.dumps(discord_data))
        self.media = []
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
        self.client = Mastodon(
            client_id=self.consumer_key,
            client_secret=self.consumer_secret,
            access_token=self.token,
            api_base_url="https://mastodon.social"
        )
        response = "Logged in"
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
    def _init_keys(self, debug=False):
        self.bearer_token = TWITTER_BEARER_TOKEN
        self.consumer_key = TWITTER_CONSUMER_KEY
        self.consumer_secret = TWITTER_CONSUMER_SECRET
        self.token = TWITTER_OAUTH_TOKEN
        self.oauth_secret = TWITTER_OAUTH_SECRET
        if debug:
            print("consumer_key   :", self.consumer_key)
            print("consumer_secret:", self.consumer_secret)
            print("token          :", self.token)
            print("oauth_secret   :", self.oauth_secret)

    def login(self):
        client = tweepy.Client(bearer_token=self.bearer_token, consumer_key=self.consumer_key, consumer_secret=self.consumer_secret, access_token=self.token, access_token_secret=self.oauth_secret)
        tweepy_v1_auth = tweepy.OAuth1UserHandler(self.consumer_key, self.consumer_secret, self.token, self.oauth_secret)
        tweepy_v1 = tweepy.API(tweepy_v1_auth)
        self.client = client
        self.upload_client = tweepy_v1

    def upload_media(self, media_path=None, media_url=None, media_bytes=None):
        if media_bytes:
            print("Bytes are currently unsupported.")
            return False
        if media_url:
            print("External media is currently unsupported.")
            return False
        if media_path:
            media = self.upload_client.media_upload(media_path)
            if media:
                self.media.append(media.media_id_string)
            self.log_response(media)
        return media

    def post(self, body, title="", tags=""):
        if tags:
            body += self.clean_hashtags(tags)
        if self.media:
            response = self.client.create_tweet(media_ids=self.media, in_reply_to_tweet_id=None, text=body)
        else:
            response = self.client.create_tweet(in_reply_to_tweet_id=None, text=body)
        self.uploaded_media = []
        self.log_response(response)
        return response

    def boost(self, post_id):
        return {"reminder": "Twitter Boosting is unavailable."}

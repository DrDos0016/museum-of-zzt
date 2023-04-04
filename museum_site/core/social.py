import os
import time

from museum_site.constants import APP_ROOT

import pytumblr

from mastodon import Mastodon
from twitter import *

from museum_site.private import (
    MASTODON_CLIENT_KEY,
    MASTODON_CLIENT_SECRET,
    MASTODON_ACCESS_TOKEN,
    MASTODON_EMAIL,
    MASTODON_PASS,

    TUMBLR_OAUTH_CONSUMER,
    TUMBLR_OAUTH_CONSUMER_SECRET,
    TUMBLR_OAUTH_TOKEN,
    TUMBLR_OAUTH_SECRET,

    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    TWITTER_OAUTH_TOKEN,
    TWITTER_OAUTH_SECRET,
)


class Social():
    """ Base Class - Do not use directly """
    reply_to = None
    response_history = []
    media = []

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
        if clear_history:
            self.response_history = []

    def reset_media(self):
        self.media = []


class Social_Mastodon(Social):
    def _init_keys(self):
        self.consumer_key = MASTODON_CLIENT_KEY
        self.consumer_secret = MASTODON_CLIENT_SECRET
        self.token = MASTODON_ACCESS_TOKEN
        self.email = MASTODON_EMAIL
        self.password = MASTODON_PASS

    def login(self):
        self.client =  Mastodon(client_id=os.path.join(APP_ROOT, "wozzt-mastodon.secret"))
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


    def post(self, body):
        if self.media:
            media = []
            for m in self.media:
                media.append(m["id"])
        else:
            media=None
        response = self.client.status_post(status=body, in_reply_to_id=self.reply_to, media_ids=media)

        self.log_response(response)
        return response

    def boost(self, post_id):
        response = self.client.status_reblog(str(post_id))
        self.log_response(response)
        return response


class Social_Tumblr(Social):
    uploaded_media = []

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

    def post(self, body):
        print("BODY", body)
        if self.uploaded_media:
            response = self.client.create_photo("worldsofzzt", state="published", caption=body, data=self.uploaded_media)
        else:
            response = self.client.create_text("worldsofzzt", state="published", body=body)
        self.log_response(response)
        return response

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
        self.client = Twitter(auth=OAuth(self.token, self.oauth_secret, self.consumer_key, self.consumer_secret))
        self.upload_client = Twitter(domain='upload.twitter.com', auth=OAuth(self.token, self.oauth_secret, self.consumer_key, self.consumer_secret))

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

    def post(self, body):
        if self.media:
            media = ",".join(self.media)
        else:
            media=""

        response = self.client.statuses.update(status=body, media_ids=media, in_reply_to_status_id=self.reply_to, tweet_mode="extended")
        self.log_response(response)
        return response

    def boost(self, post_id):
        post_id = str(post_id)
        # Must un-retweet to prevent errors for re-retweet attempts
        response = self.client.statuses.unretweet(id=post_id)
        self.log_response(response)
        time.sleep(0.5)  # Probably not necessary
        response = self.client.statuses.retweet(id=post_id)
        self.log_response(response)
        return response

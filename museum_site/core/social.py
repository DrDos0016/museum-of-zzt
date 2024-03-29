import os
import time

from museum_site.constants import APP_ROOT, HOST, APP_ROOT

import pytumblr

from cohost.models.user import User
from cohost.models.block import MarkdownBlock
from mastodon import Mastodon
from twitter import *

from museum_site.settings import (
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

    COHOST_COOKIE,
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
        # Default hashtag handler. Works for Cohost and Tumblr.
        # IN: "#zzt, #museum of zzt, #ascii" OUT: ["zzt" , "museum of zzt", "ascii"]
        cohost_hashtags_list = []
        raw_tags = tags
        tags = raw_tags.split(",")
        for tag in tags:
            tag = tag.strip()
            if tag.startswith("#"):
                cohost_hashtags_list.append(tag[1:])
        return cohost_hashtags_list

class Social_Cohost(Social):
    """ https://pypi.org/project/cohost/ """
    def _init_keys(self):
        self.cookie = COHOST_COOKIE

    def login(self):
        self.user = User.loginWithCookie(self.cookie)
        self.project = self.user.getProject("worldsofzzt")

    def upload_media(self, media_path=None, media_url=None, media_bytes=None):
        if media_bytes:
            print("Bytes are currently unsupported.")
            return False
        if media_url:
            print("External media is currently unsupported.")
            return False
        if media_path:
            full_media_path = HOST[:-1] + media_path
            self.media.append("<a href='{}' target='_blank'><img src='{}'></a>".format(full_media_path, full_media_path))

    def post(self, body, title="", tags=[]):
        blocks = []
        # Attach media if any has been specified
        if self.media:
            # ZAP Form adds full filepath, but Cohost wants the path as a URL for hotlinking hence the replace() call
            media_string = "\n".join(self.media).replace(APP_ROOT, "")
            body = media_string + "\n" + body

        # Attach hashtags
        if tags:
            tags = self.clean_hashtags(tags)

        # Attach post
        blocks.append(MarkdownBlock(body))

        # Chost
        response = self.project.post(title, blocks, tags=tags)

        self.media = []
        self.uploaded_media = []
        self.log_response(response.url)
        return response



class Social_Mastodon(Social):
    def _init_keys(self):
        self.consumer_key = MASTODON_CLIENT_KEY
        self.consumer_secret = MASTODON_CLIENT_SECRET
        self.token = MASTODON_ACCESS_TOKEN
        self.email = MASTODON_EMAIL
        self.password = MASTODON_PASS

    def login(self):
        self.client =  Mastodon(client_id=MASTODON_SECRETS_FILE)
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


    def post(self, body, title="", tags=[]):
        if self.media:
            media = []
            for m in self.media:
                media.append(m["id"])
        else:
            media=None
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

    def post(self, body, title="", tags=[]):
        # Attach hashtags
        if tags:
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

    def post(self, body, title="", tags=[]):
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

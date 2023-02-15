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
        response_history.append(response)

    def get_last_response(self):
        return self.response_history[-1]

    def reset(self, clear_history=True):
        self.reply_to = None
        self.media = []
        if clear_history:
            self.response_history = []


class Social_Mastodon(Social):
    def _init_keys(self):
        self.consumer_key = MASTODON_CLIENT_KEY
        self.consumer_secret = MASTODON_CLIENT_SECRET
        self.token = MASTODON_ACCESS_TOKEN
        self.email = MASTODON_EMAIL
        self.password = MASTODON_PASS

    def login(self):
        self.client =  Mastodon(client_id=os.path.join(SITE_ROOT, "museum_site", "wozzt-mastodon.secret"))
        self.client.log_in(MASTODON_EMAIL, MASTODON_PASS)

    def upload_media(self, media_path=None, media_url=None, media_bytes=None):
        if media_bytes:
            print("Bytes are currently unsupported.")
            return False
        if media_url:
            path("External media is currently unsupported.")
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
        response = self.client.status_post(status=body, in_reply_to=self.reply_to, media_ids=media)

        self.log_response(response)
        return response


class Social_Tumblr(Social):
    def _init_keys(self):
        self.consumer_key = TUMBLR_OAUTH_CONSUMER,
        self.consumer_secret = TUMBLR_OAUTH_CONSUMER_SECRET
        self.token = TUMBLR_OAUTH_TOKEN
        self.oauth_secret = TUMBLR_OAUTH_SECRET

    def login(self):
        self.client = pytumblr.TumblrRestClient(self.consumer_key, self.consumer_secret, self.token, self.oauth_secret)


class Social_Twitter(Social):
    def _init_keys(self):
        self.consumer_key = TWITTER_CONSUMER_KEY
        self.consumer_secret = TWITTER_CONSUMER_SECRET
        self.token = TWITTER_OAUTH_TOKEN
        self.oauth_secret = TWITTER_OAUTH_SECRET

    def login(self):
        self.client = Twitter(auth=OAuth(self.token, self.oauth_secret, self.consumer_key, self.consumer_secret))
        self.upload_client = Twitter(domain='upload.twitter.com', auth=OAuth(self.token, self.oauth_secret, self.consumer_key, self.consumer_secret))

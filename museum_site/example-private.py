# Internet Archive
# https://archive.org/services/docs/api/index.html
# https://archive.org/account/s3.php
# Used for mirroring uploaded files to the Internet Archive.
IA_ACCESS = ""
IA_SECRET = ""

# Patreon
# Beta site credentials are displayed on user profiles for Patrons
# Password values are used for non-logged in patrons to access articles with
# "upcoming" status for $2 and "upcoming"/"unpublished" status for $5.
BETA_USERNAME = ""
BETA_PASSWORD = ""
PASSWORD2DOLLARS = ""
PASSWORD5DOLLARS = ""

# Twitter
# https://developer.twitter.com/en/apps
TWITTER_CONSUMER_KEY = ""
TWITTER_CONSUMER_SECRET = ""
TWITTER_OAUTH_TOKEN = ""
TWITTER_OAUTH_SECRET = ""

# Discord Webhooks
# Server Settings -> Integrations -> Webhooks
# Used for the Worlds of ZZT Discord to track Worlds of ZZT bot tweets.
# Upload webhook used to annouce new file uploads (not yet implemented)
WEBHOOK_URL = ""
NEW_UPLOAD_WEBHOOK_URL = ""

# IP Bans
# TODO: This is janky and temporary
# IPs listed here are compared against the REMOTE_ADDR HTTP header preventing
# reviewing or uploading of files
BANNED_IPS = [
    "",
]

# Patrons
# These names will appear on the site credits page unless an account marked as
# a patron has the same patron email as the one listed here. When an
# unregistered Patron registers they may be removed from this list.
UNREGISTERED_SUPPORTERS = [
    {
        "name": "ZZT", "char": 2, "fg": "white", "bg": "darkblue",
        "email": "zzt@example.com"
    },
]

UNREGISTERED_BIGGER_SUPPORTERS = [
    {
        "name": "Super ZZT", "char": 2, "fg": "white", "bg": "darkblue",
        "email": "superzzt@museumofzzt.com"
    },
]

UNREGISTERED_BIGGEST_SUPPORTERS = [
    {
        "name": "Super Duper ZZT", "char": 2, "fg": "white", "bg": "darkblue",
        "email": "superduperzzt@museumofzzt.com"
    },
]

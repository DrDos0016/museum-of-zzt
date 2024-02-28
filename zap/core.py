import json
import os

from datetime import datetime, timezone
from museum_site.constants import STATIC_PATH
from museum_site.core.social import Social_Mastodon, Social_Twitter, Social_Tumblr, Social_Cohost

ZAP_UPLOAD_PATH = os.path.join(STATIC_PATH, "zap", "media")
ZAP_STATIC_PATH = "/static/zap/media/"


def querydict_to_json_str(qd):
    IGNORED_KEYS = ("csrfmiddlewaretoken", )
    raw = {}

    for k in qd:
        if k in IGNORED_KEYS:
            continue
        v = qd.getlist(k)
        if len(v) == 1:
            raw[k] = v[0]
        if len(v) > 1:
            raw[k] = v

    output = json.dumps(raw, sort_keys=True)
    return output


def zap_upload_file(uploaded_file, requested_file_name=""):
    print(uploaded_file)
    now = datetime.now(timezone.utc)
    year_str = str(now)[:4]
    month_str = str(now)[5:7]
    requested_file_name = uploaded_file.name if not requested_file_name else requested_file_name
    file_static_path = os.path.join(year_str, month_str, requested_file_name)
    output_path = os.path.join(ZAP_UPLOAD_PATH, file_static_path)
    with open(output_path, "wb+") as fh:
        for chunk in uploaded_file.chunks():
            fh.write(chunk)
    return file_static_path


def zap_get_social_account(account):
    if account == "mastodon":
        s = Social_Mastodon()
    elif account == "twitter":
        s = Social_Twitter()
    elif account == "tumblr":
        s = Social_Tumblr()
    elif account == "cohost":
        s = Social_Cohost()
    return s

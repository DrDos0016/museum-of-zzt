import json
import os

from datetime import datetime, timezone

ZAP_UPLOAD_PATH = "/var/projects/museum-of-zzt/museum_site/static/zap/media/"


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
    output_path = os.path.join(ZAP_UPLOAD_PATH, year_str, month_str, requested_file_name)
    print("PATH", output_path)
    with open(output_path, "wb+") as fh:
        for chunk in uploaded_file.chunks():
            fh.write(chunk)
    print("Wrote file: ", output_path)

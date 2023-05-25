import glob
import json
import os
import sys
import urllib.request

from datetime import datetime

import django
import requests

django.setup()

from museum_site.constants import DATA_PATH  # noqa: E402
from museum_site.models import *  # noqa: E402
from museum_site.core.detail_identifiers import *  # noqa: E402

TEST_ARCHIVE_LINKS = True if "iatest" in sys.argv else False


def main():
    qs = File.objects.all().order_by("-id")
    all_issues = []
    output = {
        "meta": {
            "started": str(datetime.now()),
        }
    }
    for zf in qs:
        print(zf.id)
        issues = zf.scan()

        if issues:
            issues["pk"] = zf.pk

        all_issues.append(issues)

    output["issues"] = all_issues
    output["meta"]["finished"] = str(datetime.now())

    with open(os.path.join(DATA_PATH, "scan.json"), "w") as fh:
        fh.write(json.dumps(output))

    return True


if __name__ == "__main__":
    main()

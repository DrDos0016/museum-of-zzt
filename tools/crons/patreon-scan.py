import json
import os
import requests
import sys

import django

from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402
from private_patreon import *  # noqa: E402


def main():
    print("Starting...")
    print(str(datetime.now())[:19])

    r = get_campaign_members()

    while True:
        if r["success"]:
            data = r["resp"]["data"]
            for patron in data:
                email = patron["attributes"]["email"]
                status = str(patron["attributes"]["patron_status"])
                status = status.split("_")[0]
                pledge = (
                    patron["attributes"]["currently_entitled_amount_cents"]
                )
                last_date = patron["attributes"]["last_charge_date"]
                last_status = patron["attributes"]["last_charge_status"]
                # print(pledge, status, last_date, last_status, email)

                if status == "active":
                    qs = User.objects.filter(
                        email=email, is_active=True
                    ).only("id")
                    if qs:
                        profile = Profile.objects.get(user_id=qs[0].id)
                        profile.patron = True
                        profile.patron_level = pledge
                        profile.save()
                        print("Marked", profile, "as Patron")
        else:
            break

        if r["resp"].get("links"):
            r = get_campaign_members(r["resp"]["links"]["next"])
        else:
            break

    print("DONE.")
    return True


def get_campaign_members(url=None):
    if url is None:
        url = (
            "https://www.patreon.com/api/oauth2/v2/campaigns/"
            "{}/members".format(WOZZT_CAMPAIGN_ID)
        )
        qs = (
            "?include=currently_entitled_tiers&fields[member]=patron_status,"
            "email,currently_entitled_amount_cents,last_charge_date,"
            "last_charge_status"
        )
        full_url = url + qs
    else:
        full_url = url
    headers = {"Authorization": "Bearer {}".format(PATREON_ACCESS_TOKEN)}
    r = requests.get(full_url, headers=headers)

    return process_response(r)


def process_response(r):
    # print(json.dumps(r.json(), indent=4, sort_keys=True))

    if r.status_code == 200:
        return {"success": True, "resp": r.json()}
    else:
        return {"success": False, "status": r.status_code, "resp": r.content}


if __name__ == '__main__':
    main()

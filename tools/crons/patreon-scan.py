import json
import os
import requests
import sys

import django

from datetime import datetime

#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402

PATREON_CLIENT_ID = os.environ.get("MOZ_PATREON_CLIENT_ID", "-UNDEFINED-")
PATREON_CLIENT_SECRET = os.environ.get("MOZ_PATREON_CLIENT_SECRET", "-UNDEFINED-")
PATREON_ACCESS_TOKEN = os.environ.get("MOZ_PATREON_ACCESS_TOKEN", "-UNDEFINED-")
PATREON_REFRESH_TOKEN = os.environ.get("MOZ_PATREON_REFRESH_TOKEN", "-UNDEFINED-")
WOZZT_CAMPAIGN_ID = os.environ.get("MOZ_PATREON_CAMPAIGN_ID", "-UNDEFINED-")


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
                pledge = patron["attributes"]["currently_entitled_amount_cents"]
                last_date = patron["attributes"]["last_charge_date"]
                last_status = patron["attributes"]["last_charge_status"]
                tier_id = 0
                if patron["relationships"]["currently_entitled_tiers"]["data"]:
                    tier_id = patron["relationships"]["currently_entitled_tiers"]["data"][0]["id"]

                #print(pledge, status, last_date, last_status, email)

                if status == "active":
                    qs = User.objects.filter(profile__patron_email=email, is_active=True).only("id")
                    if qs:
                        profile = Profile.objects.get(user_id=qs[0].id)
                        was_patron = profile.patron
                        old_pledge = profile.patronage
                        profile.patron = True
                        profile.patronage = pledge

                        if not was_patron or (old_pledge != profile.patronage):
                            print(tier_id)
                            if tier_id:
                                profile.patron_tier = tier_id
                            profile.save()
                            print("Marked", profile, "as Patron with pledge of", pledge, "tier", tier_id)
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
        url = "https://www.patreon.com/api/oauth2/v2/campaigns/{}/members".format(WOZZT_CAMPAIGN_ID)
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

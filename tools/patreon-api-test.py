import json
import os
import requests
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User

from museum_site.models import *  # noqa: E402
from private import *


def main():
    print("Starting...")

    #print("Getting Identity")
    #get_identity()

    #print("Getting campaigns")
    #get_campaign()

    r = get_campaign_members()
    if r["success"]:
        data = r["resp"]["data"]
        for patron in data:
            #print(json.dumps(patron, indent=4, sort_keys=True))
            email = patron["attributes"]["email"]
            status = patron["attributes"]["patron_status"].split("_")[0]
            pledge = patron["attributes"]["currently_entitled_amount_cents"]
            last_date = patron["attributes"]["last_charge_date"]
            last_status = patron["attributes"]["last_charge_status"]
            print(pledge, "\t", status, last_date, last_status, "\t\t", email)

            if status == "active":
                qs = User.objects.filter(email=email).only("id")
                if qs:
                    profile = Profile.objects.get(user_id=qs[0].id)
                    profile.patron = True
                    profile.patron_level = pledge
                    profile.save()
                    print("Marked", profile, "as Patron")

    print("DONE.")
    return True

def get_identity():
    url = "https://www.patreon.com/api/oauth2/v2/identity"
    qs = "?fields[user]=about,created,email,first_name,full_name,image_url,last_name,social_connections,thumb_url,url,vanity"
    headers = {"Authorization": "Bearer {}".format(PATREON_ACCESS_TOKEN)}
    r = requests.get(url + qs, headers=headers)
    return process_response(r)


def get_campaign():
    url = "https://www.patreon.com/api/oauth2/v2/campaigns"
    headers = {"Authorization": "Bearer {}".format(PATREON_ACCESS_TOKEN)}
    r = requests.get(url, headers=headers)
    return process_response(r)


def get_campaign_members():
    url = "https://www.patreon.com/api/oauth2/v2/campaigns/{}/members".format(WOZZT_CAMPAIGN_ID)
    qs = "?include=currently_entitled_tiers&fields[member]=patron_status,email,currently_entitled_amount_cents,last_charge_date,last_charge_status"
    headers = {"Authorization": "Bearer {}".format(PATREON_ACCESS_TOKEN)}
    r = requests.get(url + qs, headers=headers)
    return process_response(r)

    """
    // Sample response for (url decoded) https://www.patreon.com/api/oauth2/v2/campaigns/{campaign_id}/members
    ?include=currently_entitled_tiers,address
    &fields[member]=full_name,is_follower,last_charge_date,last_charge_status,lifetime_support_cents,currently_entitled_amount_cents,patron_status
    &fields[tier]=amount_cents,created_at,description,discord_role_ids,edited_at,patron_count,published,published_at,requires_shipping,title,url
    &fields[address]=addressee,city,line_1,line_2,phone_number,postal_code,state
    """


def process_response(r):
    if r.status_code == 200:
        return {"success": True, "resp": r.json()}
    else:
        return {"success": False, "status": r.status_code, "resp": r.content}



if __name__ == '__main__':
    main()


import json
import os
import random
import sys
import zipfile
from datetime import datetime
from urllib.parse import quote

import django
#import pytumblr
import requests
from twitter import *
from PIL import Image

sys.path.append("/var/projects/museum")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import (
    File, DETAIL_ZZT, DETAIL_SZZT, DETAIL_UPLOADED, DETAIL_GFX, DETAIL_LOST
)

import zookeeper

from private import (
    CONSUMER, SECRET, OAUTH_TOKEN, OAUTH_SECRET, TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET, TWITTER_OAUTH_TOKEN, TWITTER_OAUTH_SECRET,
    WEBHOOK_URL
)

from blacklist import BLACKLISTED_FILES, BLACKLISTED_BOARDS, BOARD_TITLE_BLACKLIST


def main():
    POST = True if "NOPOST" not in sys.argv else False
    CRON_ROOT = "/var/projects/museum/tools/crons/"
    ROOT = "/var/projects/museum"
    QUEUE = os.path.join(CRON_ROOT, "woz_queue.txt")
    APRIL = True if datetime.now().strftime("%m-%d") == "04-01" else False

    # Check if there's anything in the manual queue
    """ Queue Format: YYYY-MM-DD:HOUR:PK:FILENAME:BOARD
        Use * for wildcards in dates/hours
        Keep wildcard dates/hours below specific ones to allow first match
         1:45 AM == 9
         5:45 AM == 12
         8:45 AM == 15
        11:45 AM == 18
         2:45 PM == 21
         5:45 PM == 0
         8:45 PM == 3
        11:45 PM == 6
    """
    source = "RANDOM"
    queue_data = {}
    output = ""
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_hour = datetime.now().strftime("%H")
    print("DATE/HOUR", current_date, current_hour)

    if os.path.isfile(QUEUE):
        with open(QUEUE) as fh:
            lines = fh.readlines()
    else:
        lines = []

    for line in lines:
        line = line.strip()
        print("LINE", line)

        if line.strip() != "":
            date, hour, pk, filename, board = line.split(":")
            # Do we use this?
            if (source == "RANDOM") and ((date == "*" or date == current_date) and (hour == "*" or hour == current_hour)):
                source = "QUEUE"
                queue_data = {"pk":int(pk), "filename":filename, "board":int(board)}
            else: # if we don't use it, add it to the output text file
                output += line + "\n"
    print("---")

    # Write the new queue
    output = output[:-1]
    with open(QUEUE, "w") as fh:
        fh.write(output)

    print("SOURCE IS", source)
    print("DATA IS", queue_data)

    if source == "RANDOM":
        # Select a random zip
        # - Zip must have a ZZT World in it and be published
        # - Zip must not have modified graphics
        qs = File.objects.filter(details__in=[DETAIL_ZZT]).exclude(details__in=[DETAIL_UPLOADED, DETAIL_GFX, DETAIL_LOST]).order_by("?")

        # Filter out blacklisted files
        for file_obj in qs:
            data = file_obj
            if data.id not in BLACKLISTED_FILES:
                break

        # Pull related articles in preparation of linking them later
        related_articles = data.articles.filter(published=True).order_by("date")

        # Select a random ZZT file in the zip
        zip = zipfile.ZipFile(ROOT + data.download_url())
        files = zip.namelist()
        files.sort()

        world_choices = []
        for file in files:
            filename = file.lower()
            if filename.endswith(".zzt"):
                world_choices.append(file)

        if not world_choices:
            abort("ERROR: World choices was empty for", file.id)

        selected = random.choice(world_choices)
        print(selected)

        # Extract it
        zip.extract(selected, CRON_ROOT)

        # Figure out if it's Title Screen Tuesday
        now = datetime.now()
        if int(now.strftime("%w")) == 2:
            tuesday = True
        else:
            tuesday = False

        # Parse the world with Zookeeper
        z = zookeeper.Zookeeper(os.path.join(CRON_ROOT, selected))

        # Select a random board (unless it's Tuesday)
        processing = True
        board_name = ""
        bl_key = str(data.id) + ":" + selected  # Blacklist key
        bl = BLACKLISTED_BOARDS.get(bl_key, [])

        while processing:
            if tuesday:
                board_num = 0
                processing = False
                if (0 in BLACKLISTED_BOARDS.get(bl_key, [])):
                    # In case the title screen is blacklisted and it's tuesday
                    tuesday = False
                    processing = True

            if not tuesday:
                board_num = random.randint(0, len(z.boards) - 1)

            # Verify the board isn't a common toolkit
            if processing and z.boards[board_num].title in BOARD_TITLE_BLACKLIST:
                continue

            # Verify the board isn't in the board blacklist
            if processing and board_num in bl:
                continue

            z.boards[board_num].screenshot(CRON_ROOT + "temp", title_screen=(board_num == 0))
            board_name = z.boards[board_num].title

            # Board properties
            board_properties = []
            # Dark
            if z.boards[board_num].is_dark:
                board_properties.append("🔦")
            # Zap
            if z.boards[board_num].zap:
                board_properties.append("⚡")
            # Can fire
            if z.boards[board_num].can_fire != 255:
                board_properties.append(str(z.boards[board_num].can_fire) + " 🔫")
            # Time limit
            if z.boards[board_num].time_limit != 0:
                board_properties.append(str(z.boards[board_num].time_limit) + " ⏳")


            processing = False
    elif source == "QUEUE":
        tuesday = False

        # Pull the zip
        data = File.objects.get(pk=queue_data["pk"])
        selected = queue_data["filename"]
        board_num = queue_data["board"]

        # Select the ZZT file in the zip
        zip = zipfile.ZipFile(ROOT + data.download_url())

        # Extract it
        zip.extract(queue_data["filename"], CRON_ROOT)

        # Parse the world with Zookeeper
        z = zookeeper.Zookeeper(os.path.join(CRON_ROOT, queue_data["filename"]))

        # Render
        z.boards[queue_data["board"]].screenshot(CRON_ROOT + "temp", title_screen=(queue_data["board"] == 0), dark=APRIL)
        board_name = z.boards[queue_data["board"]].title

        # Board properties
        board_properties = []
        # Dark
        if z.boards[queue_data["board"]].is_dark:
            board_properties.append("🔦")
        # Zap
        if z.boards[queue_data["board"]].zap:
            board_properties.append("⚡")
        # Can fire
        if z.boards[queue_data["board"]].can_fire != 255:
            board_properties.append(str(z.boards[queue_data["board"]].can_fire) + " 🔫")
        # Time limit
        if z.boards[queue_data["board"]].time_limit != 0:
            board_properties.append(str(z.boards[queue_data["board"]].time_limit) + " ⏳")

    bp = ""
    if board_properties:
        bp = " {"
        for p in board_properties:
            bp += p + ", "
        bp = bp[:-2] + "}"



    # Remove the ZZT file. We're done with it.
    try:
        os.remove(os.path.join(CRON_ROOT, selected))
    except:
        abort("Couldn't remove:", selected)

    # Prepare the posts
    # Tumblr
    """
    tumblr_post = "<b>{title}</b> by <i>{author}</i>"
    if data.release_date:
        tumblr_post += " ({year})"
    if data.company:
        tumblr_post += "<br>\nPublished by: {company}"
    tumblr_post += "<br>\n"
    tumblr_post += "[{zzt_file}] - {board_title}<br>\n"
    tumblr_post += "<a href='https://museumofzzt.com{file_url}"
    tumblr_post += "?file={zzt_file}&board={board_idx}'>Download / Explore {zip_file} "
    tumblr_post += "on the Museum of ZZT</a><br>\n"
    if data.archive_name:
        tumblr_post += "<a href='https://museumofzzt.com{play_url}'>Play Online</a><br>\n"

    tumblr_post = tumblr_post.format(
        title=data.title,
        author=data.author,
        year=str(data.release_date)[:4],
        company=data.company,
        zzt_file=quote(selected),
        board_title=z.boards[board_num].title,
        file_url=quote(data.file_url()),
        board_idx=board_num,
        zip_file=data.filename,
        play_url=quote(data.play_url())
    )

    # Tumblr - Related Articles
    if len(related_articles) > 0:
        article_text = "<br>"
        for article in related_articles[:3]:
            article_text += "<a href='https://museumofzzt.com{url}'>{text}</a><br>\n"
            article_text = article_text.format(
                url=article.url(),
                text=article.title
            )
        tumblr_post += article_text

    # Tumblr - Tags
    tags = ["ZZT", data.author, data.title, data.filename]

    if tuesday:
        tags.append("title screen tuesday")
    print(tumblr_post)

    client = pytumblr.TumblrRestClient(CONSUMER, SECRET, OAUTH_TOKEN, OAUTH_SECRET)
    """

    if POST:
        """
        print("Posting to tumblr...")
        print(tags)
        resp = client.create_photo("worldsofzzt", state="published", tags=tags, caption=tumblr_post, data=(CRON_ROOT + "temp.png"))
        print(resp)
        """

        # Twitter
        twitter_post = "https://museumofzzt.com{file_url}"
        twitter_post += "?file={zzt_file}&board={board_idx}\n"
        twitter_post += "{title} by {author}"
        if data.release_date:
            twitter_post += " ({year})"
        if data.company:
            twitter_post += "\nPublished by: {company}"
        twitter_post += "\n[{zzt_file}] - \"{board_title}\"{board_properties}"
        if data.archive_name:
            twitter_post += "\nhttps://museumofzzt.com{play_url}"

        twitter_post = twitter_post.format(
            file_url=quote(data.file_url()),
            zzt_file=quote(selected),
            board_idx=board_num,
            board_title=z.boards[board_num].title,
            board_properties=bp,
            title=data.title,
            author=data.author,
            year=str(data.release_date)[:4],
            company=data.company,
            play_url=quote(data.play_url()),
        )


        print(twitter_post)
        print("Posting to twitter...")

        # April
        #if APRIL:
        #    twitter_post = "Room is dark - you need to light a torch!\n" + twitter_post

        with open(CRON_ROOT + "temp.png", "rb") as imagefile:
            imagedata = imagefile.read()

            t_up = Twitter(domain='upload.twitter.com', auth=OAuth(TWITTER_OAUTH_TOKEN, TWITTER_OAUTH_SECRET, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET))
            img1 = t_up.media.upload(media=imagedata)["media_id_string"]
            t = Twitter(auth=OAuth(TWITTER_OAUTH_TOKEN, TWITTER_OAUTH_SECRET, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET))
            resp = t.statuses.update(status=twitter_post, media_ids=img1, tweet_mode="extended")
            print(resp)
            twitter_id = resp.get("id")
            twitter_img = resp["entities"]["media"][0]["media_url"]

        # Twitter - Related Articles
        if len(related_articles) > 0:
            article_text = "For more related content about \"{title}\", check out:\n".format(title=data.title)
            for article in related_articles[:3]:
                article_text += "https://museumofzzt.com" + article.url() + "\n"

            resp = t.statuses.update(status=article_text, in_reply_to_status_id=twitter_id)

        # Discord webhook
        discord_post = "https://twitter.com/worldsofzzt/status/{}\n**{}** by {} ({})\n"
        if data.company:
            discord_post += "Published by: {}\n".format(data.company)
        discord_post += "`[{}] - \"{}\"` {}\n"
        discord_post += "Explore: https://museumofzzt.com" + quote(data.file_url()) + "?file=" + quote(selected) + "&board=" + str(board_num) + "\n"
        if data.archive_name:
            discord_post += "Play: https://museumofzzt.com" + quote(data.play_url())

        discord_post = discord_post.format(twitter_id, data.title, data.author, str(data.release_date)[:4], selected, z.boards[board_num].title, bp)

        discord_data = {
            "content": discord_post,
            "embeds": [
                {"image": {"url": twitter_img}}
            ]
        }
        resp = requests.post(WEBHOOK_URL, headers={"Content-Type": "application/json"}, data=json.dumps(discord_data))
        print(resp)
        print(resp.content)

    else:
        print("DID NOT POST")

    return True

def abort(msg):
    print(msg)
    sys.exit()

if __name__ == "__main__":
    main()

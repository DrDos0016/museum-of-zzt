import os
import sys

import django

from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402

def update_article(a):
    soup = BeautifulSoup(a.content, "html.parser")

    # Youtube-embed class
    tags = soup.find_all("div", {"class": "youtube-embed"})
    if tags:
        #print(tags)
        for tag in tags:
            tag_str = str(tag)
            start = tag_str.find("/embed/")
            end = tag_str.find("?")
            if start and end and len(tags) == 1:
                video_id = tag_str[start + 7:end]
                #print("VIDEO ID", video_id)
                replacement = "{% youtube_embed '" + video_id + "' %}"

                c_start = a.content.find('<div class="youtube-embed">')
                c_end = a.content.find("</div>")

                c = (a.content[:c_start] + replacement + a.content[c_end + 7:]).strip()
                a.content = c
                a.save()

                #print(c)
                #input("HOLD")
                return True
            else:
                print("???", tag)
                return False

    # Try more generic div class="c"
    tags = soup.find_all("div", {"class": "c"})
    if tags:
        #print(tags)
        for tag in tags:
            tag_str = str(tag)
            start = tag_str.find("/embed/")
            end = tag_str.find("?")
            if start and end and len(tags) == 1:
                video_id = tag_str[start + 7:end]
                #print("VIDEO ID", video_id)
                replacement = "{% youtube_embed '" + video_id + "' %}"

                c_start = a.content.find('<div class="c">')
                c_end = a.content.find("</div>")

                c = (a.content[:c_start] + replacement + a.content[c_end + 7:]).strip()
                a.content = c
                a.save()

                #print(c)
                #input("HOLD")
                return True
            else:
                print("???", tag)
                return False

    return False


def main():
    fh = open("urls.html", "w")
    fh.write("<ol>\n")
    qs = Article.objects.all().order_by("-pk")
    #qs = Article.objects.filter(pk=1086)
    to_update = []
    successes = 0
    for a in qs:
        has_yt_url = " "
        has_yt_embed = " "
        if "youtube.com" in a.content:
            has_yt_url = "X"
            if "youtube.com/embed/" in a.content:
                has_yt_embed = "X"

            if has_yt_url == "X" and has_yt_embed == "X":
                print("[{}][{}][{}] {}".format(has_yt_url, has_yt_embed, a.category, a))
                to_update.append(a)

    print("I want to update {} articles".format(len(to_update)))
    input("HOLD")

    for a in to_update:
        updated = update_article(a)
        if updated:
            successes += 1
            print("Updated", a)
            fh.write("<li><a href='http://django.pi:8000{}' target='_blank'>{}</a> UPDATED</li>\n".format(a.get_absolute_url(), a))
        else:
            print("DID NOT UPDATE", a)
            fh.write("<li><a href='http://django.pi:8000{}' target='_blank'>{}</a> DID NOT UPDATE</li>\n".format(a.get_absolute_url(), a))

    fh.write("<ol>\n")
    fh.close()

    #"{% youtube_embed '{}' %}"
    print("I updated {} articles".format(successes))
    return True


if __name__ == '__main__':
    main()

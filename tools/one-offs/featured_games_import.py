# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import django, sys, os, json

sys.path.append("/var/projects/z2/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from z2_site.models import *

def main():
    """
    This imports a json dump of z2's featured games table into the new z2's article system.

    It DOES NOT associate these articles with their game.
    """

    with open("fg.json") as raw:
        fgs = json.loads(raw.read())
        
        for fg in fgs:
            article = Article()
            article.title = "Featured Game: " + fg["gamefile"]
            article.author = fg["reviewer"]
            article.category = "Featured Game"
            article.content = fg["review"]
            article.css = ""
            article.date = "1970-01-01"
            article.published = True
            article.type = "html"
            article.page = 1
            
            article.save()
            print("Saved", article.title)

    return True
    
if __name__ == "__main__":main()
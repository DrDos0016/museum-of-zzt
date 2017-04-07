# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import django, sys, os, codecs

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from z2_site.models import *

from datetime import datetime

""" This will need additional development """

def main():
    raw = codecs.open("reviews.csv", "r", "utf-8").readlines()
    for line in raw:
        split = line.split("☃") # this is the best delimiter ever
        if len(split) > 8:
            print("UH OH", line, "Split length: ", len(split))
            continue

        title = split[0][1:-1]
        author = split[1][1:-1]
        email = split[2][1:-1]
        review = split[3][1:-1]
        postdate = datetime.fromtimestamp(int(split[4][1:-1])).strftime('%Y-%m-%d %H:%M:%S')
        gamefile = split[5][1:-1]
        rating = split[6][1:-1]
        ip = split[7][1:-1].replace('"', "")

        # Get the file the review is for
        try:
            file_id = File.objects.get(filename=gamefile)
        except:
            print("UH OH", gamefile, " has no results")
            print("Look for a weird review with", file_id, title, author)

        #review = Review(file=file_id, title=title, author=author, email=email, content=review, rating=rating, date=str(postdate)[:10], ip=ip)
        #review.save()

        """
        file        = models.ForeignKey("File")         # Review file
        title       = models.CharField(max_length=50)   # Review title
        author      = models.CharField(max_length=50)   # Review author
        email       = models.EmailField()               # Contact info for author (hide this? Optional?)
        content     = models.TextField()
        rating      = models.FloatField(default=5.0)
        date        = models.DateField()
        ip          = models.IPAddressField()
        """

        #print split
    print("DONE.")
    return True
if __name__ == "__main__": main()

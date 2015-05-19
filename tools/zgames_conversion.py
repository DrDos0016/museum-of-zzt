#!/usr/bin/python
import os, sys
sys.path.append("/var/projects/z2")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
from z2_site.models import File

""" This will need additional development """

def main():
    raw = open("games.csv").readlines()
    for line in raw:
        split = line.split(";")
        if len(split) > 8:
            print "UH OH", line
            continue
        title = split[0][1:-1]
        author = split[1][1:-1]
        fname = split[2][1:-1]
        size = split[4][1:-1]
        genre = split[5][1:-1]
        #fg = split[6][1:-1]
        type = split[7][1:-1]
        
        file = File(title=title, author=author, filename=fname, size=size, genre=genre, category="ZZT") # For now
        file.save()
        
        """
        title       = models.CharField(max_length=80)   # Frost 1: Power
        author      = models.CharField(max_length=80)   # Zenith Nadir
        filename    = models.CharField(max_length=50)   # Respite.zip
        size        = models.IntegerField(default=0)    # Filesize in Kilobytes
        genre       = models.CharField(max_length=50)   # Action, Adventure, Puzzle, Etc.
        category    = models.CharField(max_length=10)   # ZZT, Super ZZT, ZIG, Utility, Editor, Etc.
        screenshot  = models.CharField(max_length=80)   # Screenshot of title screen
        description = models.TextField(null=True, default=None) # Description for Utilites
        details     = models.CharField(max_length=80, default="MS-DOS")
        review_count= models.IntegerField(default=0)    # Number of reviews on this file
        reviews     = models.ForeignKey("Review", null=True)    # Reviews
        """
        
        #print split
    print "DONE."
    return True
if __name__ == "__main__": main()
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import django, sys, os, codecs

sys.path.append("/var/projects/z2/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from z2_site.models import *

""" This will need additional development """

""" TO PURGE THE DB SAFELY 
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE `z2_site_file`;
DROP TABLE `z2_site_file_details`;
DROP TABLE `z2_site_review`;
SET FOREIGN_KEY_CHECKS = 1;
"""

def main():
    # (0 - ZZT, 1 - ZIG, 2 - ZZT Utility, 3 - External Utility)
    categories = {"0":"ZZT", "1":"ZIG", "2": "ZZT", "3":"Utility"}
    
    raw = codecs.open("games.csv", "r", "utf-8").readlines()
    for line in raw:
        split = line.split("☃")
        if len(split) > 8:
            print "UH OH", line
            continue
        title = split[0][1:-1]
        author = split[1][1:-1]
        fname = split[2][1:-1]
        size = split[4][1:-1]
        genre = split[5][1:-1]
        #fg = split[6][1:-1]
        type = split[7][1:-3] # (0 - ZZT, 1 - ZIG, 2 - ZZT Utility, 3 - External Utility)
        
        #"2024: Enemies";"David Hetrick";"2024enem.zip";"/zgames/1num/2024enem.zip";"3";"Shooter";"0";"0"
        
        file = File()
        
        if title[0].lower() in "abcdefghijklmnopqrstuvwxyz":
            file.letter = title[0].lower()
        else:
            file.letter = "1"
            
        file.filename       = fname
        file.title          = title
        file.author         = author.replace(", ", "/")
        file.size           = size
        file.genre          = genre.replace(", ", "/")
        file.release_date   = None
        file.release_source = None
        file.category       = categories[type]   # ZZT, Super ZZT, ZIG, Soundtrack, Utility
        
        if os.path.isfile("/var/projects/z2/assets/images/screenshots/"+file.letter+"/"+fname[:-4]+".png"):
            file.screenshot = fname[:-4]+".png"
        else:
            file.screenshot = ""
        
        file.company        = ""
        file.description    = ""
        file.review_count   = 0
        file.rating         = None
        
        file.save()
        
        print file.title
        
        #print split
    print "DONE."
    return True
if __name__ == "__main__": main()
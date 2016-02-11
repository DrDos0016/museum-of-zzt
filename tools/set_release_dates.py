#!/usr/bin/python
import os, sys, glob, zipfile, django
sys.path.append("/var/projects/z2")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()
from z2_site.models import File

SITE_ROOT = "/var/projects/z2/"

def main():
    files = File.objects.filter(release_date=None).order_by("letter", "title")
    
    for file in files:
        try:
            #print "NAME:", name
            zip = zipfile.ZipFile(SITE_ROOT + file.download_url())
            info = zip.infolist()
            
            earliest = "3000-01-01"
            
            for zfile in info:
                #print "\t" + file.filename
                if zfile.filename[-3:].upper() == "ZZT":
                    date = zfile.date_time
                    m = str(date[1])
                    d = str(date[2])
                    if date[1] < 10:
                        m = "0"+m
                    if date[2] < 10:
                        d = "0"+d
                    date_str = str(date[0])+"-"+m+"-"+d
                    if date_str < earliest:
                        earliest = date_str
                        
            if earliest != "3000-01-01":
                file.release_date = date_str
                file.release_source = "ZZT File"
                file.save()
                print ".",
        except:
            print "\nBAD FILE", file.id, file.filename + "\n"
    return True
    
if __name__ == "__main__" : main()
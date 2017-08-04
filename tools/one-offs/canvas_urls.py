#!/usr/bin/python
# coding=utf-8
import os, sys
sys.path.append("/var/projects/z2")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
from z2_site.models import File
import zipfile

""" This tool is a one-off and is designed solely for a dev environment """

def main():
    urls = ""
    files = File.objects.filter(screenshot="").order_by("letter", "filename")
    for f in files:
        letter = f.letter
        zip = f.filename
        # Open the zip
        try:
            zip = zipfile.ZipFile("/var/projects/z2/zgames/"+letter+"/"+zip) # TODO Proper path + os.path.join()
        except:
            urls += "Couldn't open zip [" + f.letter + "] - " + f.filename + "<br>"
            continue
        # Choose the file
        file_list = zip.namelist()
        
        filename = None
        for file in file_list:
            if file[-4:].lower() == ".zzt":
                filename = file
                break
        
        if not filename:
            urls += "NO .ZZT FILES FOUND IN [" + f.letter + "] - " + f.filename + "<br>"
            continue
            
        #file = zip.open(filename)
        #print "USING ZZT FILE " + filename
        
        try:
            urls += "<a href='http://django.pi:8000/file/"+f.letter+"/"+f.filename+"?file="+filename+"&board=0&screenshot=1'>"+f.letter +" - " + f.filename+"</a><br>"
        except:
            urls += "NEVERMIND, STUPID ACCENTED CHARACTER<br>"
        
    temp = open("screenshot_links.html", "w")
    temp.write(urls)
    temp.close()
    print "DONE."
    return True
if __name__ == "__main__": main()
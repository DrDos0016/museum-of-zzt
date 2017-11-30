import glob
import html
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from z2_site.models import Article


def main():
    with open("nadirposts.xml") as fh:
        xml = fh.read()
    root = ET.fromstring(xml)
    
    print(root.tag)
    print(root[0].tag)
    
    # Iterate over every <table name="nadirposts">
    page = 1
    for post in root[0]:
        article = Article()
        article.author = "Zenith Nadir"
        article.category = "Comic"
        article.type = "html"
        article.published = True
        article.page = page
        
        # Pull post info
        for child in post:
            if child.attrib.get("name") == "ID":
                print(child.text)
            elif child.attrib.get("name") == "post_title":
                print(child.text)
                article.title = child.text
            elif child.attrib.get("name") == "post_date_gmt":
                article.date = datetime.strptime(child.text[:10], "%Y-%m-%d")
            elif child.attrib.get("name") == "post_content":
                article.content = html.unescape(child.text)
                
        article.save()
        page += 1
    return True
    
if __name__ == "__main__":
    main()

import django, sys, os, json

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import *

def main():
    """
    This imports some local copies of MadTom's Pick reviews for games to be
    made featured
    """

    path = "/var/projects/museum/private/mtp/pages/awards/"
    years = ["2002", "2003", "2004"]
    months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

    for year in years:
        for month in months:
            date = year + "-" + month

            a = Article()

            try:
                with open(path + date + ".mtp") as fh:
                    content = fh.read()
                    print(content[:80].split("\n")[0])
                    name = input("Game name? ")
                    a.title = "MadTom's Pick - " + name
                    a.author = "MadTom"
                    a.category = "Featured Game"
                    a.content = content
                    a.type = "html"
                    a.date = date + "-01"
                    a.published = True
                    summary = "MadTom's Pick Review for " + name
                    a.preview = ""
            except:
                pass

            a.save()

    return True

if __name__ == "__main__":main()

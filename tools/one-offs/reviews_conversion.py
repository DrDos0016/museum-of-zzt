import django, sys, os, codecs
import json

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import *

from datetime import datetime


def from_csv():
    # This was an early review conversion script where the data had been dumped
    # to CSV format rather than JSON. It may or may not run still.
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

def from_json():
    with open("more_reviews.json") as fh:
        raw = fh.read()
        data = json.loads(raw)
        # z2 SQL columns - ip, author, postdate (timestamp), rating, review,
        # gamefile, title, email
        for z2_review in data:
            print(z2_review["gamefile"], "--", z2_review["title"])
            # Find the game this is for
            try:
                f = File.objects.get(filename=z2_review["gamefile"])
                print("\t", f)
            except:
                print("No idea what that zip is")

            # Convert!
            postdate = datetime.fromtimestamp(int(z2_review["postdate"])).strftime('%Y-%m-%d')
            review = Review(file_id=f.id, title=z2_review["title"], author=z2_review["author"], email=z2_review["email"], content=z2_review["review"], rating=z2_review["rating"], date=postdate, ip=z2_review["ip"])
            review.save()




def main():
    from_json()
    print("DONE.")
    return True
if __name__ == "__main__": main()

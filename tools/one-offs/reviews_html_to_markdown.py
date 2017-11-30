import os
import sys

import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from z2_site.models import Review


def main():
    found = 0

    for review in Review.objects.all():
        old = review.content
        review.content = review.content.replace(
            "<br />", "\n").replace(
            "<br>", "\n").replace(
            "&quot;", '"').replace(
            "&lt;i&gt;", "*").replace(
            "&lt;/i&gt;", "*")
        
        lines = review.content.split("\n")
        trimmed = []
        for line in lines:
            line = line.strip()
            trimmed.append(line)
        if trimmed[-1] == "":
            trimmed = trimmed[:-1]
        review.content = "\n".join(trimmed)
        
        if review.content != old:
            review.save()
        if (("&" in review.content)):
            print(review.id)
            found += 1
    print(found, "reviews with HTML or entities")
    return True

if __name__ == "__main__":
    main()

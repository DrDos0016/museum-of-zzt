#!/usr/bin/python
import os, sys, glob, zipfile, django
sys.path.append("/var/projects/z2")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()
from z2_site.models import File, Review

def main():
    reviews = Review.objects.all().order_by("file_id")
    
    processed = 1
    for review in reviews:
        
        file_id = review.file_id
        score = review.rating
        
        if review.file.rating is None:
            current_rating = 0
        else:
            current_rating = review.file.rating
        
        temp = current_rating * review.file.review_count
        temp += score
        
        review.file.review_count += 1
        review.file.rating = temp / review.file.review_count
        review.file.save()
        
        print processed
        processed += 1
    return True
    
if __name__ == "__main__" : main()
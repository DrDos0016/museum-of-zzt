from django.contrib.syndication.views import Feed
from django.urls import reverse
from museum_site.models import File, Article, Review, Upload

class LatestReviewsFeed(Feed):
    title = "Museum of ZZT - Latest Reviews"
    link = "/reviews/"
    description = "Museum of ZZT review feed"

    def items(self):
        return Review.objects.order_by("-id")[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content[:140]

    def item_link(self, item):
        return reverse("reviews", args=[item.file.letter, item.file.identifier]) + "#rev-" + str(item.pk)

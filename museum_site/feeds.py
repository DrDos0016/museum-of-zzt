from django.contrib.syndication.views import Feed
from django.urls import reverse

from django.template.defaultfilters import slugify

from museum_site.models import Article, File, Review
from museum_site.constants import (
    DETAIL_UPLOADED, DETAIL_LOST
)


class LatestArticlesFeed(Feed):
    title = "Museum of ZZT - Latest Articles RSS"
    link = "/articles/"
    description = "Museum of ZZT article feed"

    def items(self):
        return Article.objects.published().order_by("-id")[:25]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.summary

    def item_link(self, item):
        return reverse("article_view", args=[item.pk, slugify(item.title)])


class LatestFilesFeed(Feed):
    title = "Museum of ZZT - Latest Published Files RSS"
    link = "/files/"
    description = "Museum of ZZT published file feed"

    def items(self):
        return File.objects.published().order_by("-publish_date", "-id")[:25]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        output = "{} by {}".format(item.title, item.author)
        if item.release_date:
            output += " (" + str(item.release_date)[:4] + ")\n"
        else:
            output += "\n"
        if item.company:
            output += "Published by: " + str(item.company) + "\n"
        return output

    def item_link(self, item):
        return reverse("file", args=[item.letter, item.filename])


class LatestReviewsFeed(Feed):
    title = "Museum of ZZT - Latest Reviews RSS"
    link = "/reviews/"
    description = "Museum of ZZT review feed"

    def items(self):
        return Review.objects.order_by("-id")[:25]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        output = 'Review by {} covering "{}".'.format(
            item.get_author(), item.file.title
        )
        if item.rating >= 0:
            output += " ({}/5.0)".format(item.rating)

    def item_link(self, item):
        return reverse("reviews", args=[
            item.file.letter, item.file.filename]
        ) + "#rev-" + str(item.pk)


class LatestUploadsFeed(Feed):
    title = "Museum of ZZT - Latest Uploaded Files RSS"
    link = "/files/"
    description = "Museum of ZZT file upload feed"

    def items(self):
        return File.objects.filter(
            details__id__in=[DETAIL_UPLOADED]
        ).order_by("-id")[:25]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        output = "{} by {}".format(item.title, item.author)
        if item.release_date:
            output += " (" + str(item.release_date)[:4] + ")\n"
        else:
            output += "\n"
        if item.company:
            output += "Published by: " + str(item.company) + "\n"
        return output

    def item_link(self, item):
        return reverse("file", args=[item.letter, item.filename])

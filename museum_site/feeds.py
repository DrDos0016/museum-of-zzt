from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.template.defaultfilters import slugify

from museum_site.models import Article, File, Review


class LatestArticlesFeed(Feed):
    title = "Museum of ZZT - Latest Articles RSS"
    link = "/articles/"
    description = "Museum of ZZT article feed"

    def items(self):
        return Article.objects.published().order_by("-id")[:25]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return reverse("article_view", args=[item.pk, slugify(item.title)])


class Upcoming_Articles_Feed(LatestArticlesFeed):
    def items(self):
        return Article.objects.exclude(published=Article.REMOVED).exclude(published=Article.UNPUBLISHED).order_by("-id")[:25]


class Unpublished_Articles_Feed(LatestArticlesFeed):
    def items(self):
        return Article.objects.exclude(published=Article.REMOVED).order_by("-id")[:25]


class LatestFilesFeed(Feed):
    title = "Museum of ZZT - Latest Published Files RSS"
    link = "/files/"
    description = "Museum of ZZT published file feed"

    def items(self):
        return File.objects.published().order_by("-publish_date", "-id")[:25]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        output = "{} by {}".format(item.title, ", ".join(item.author_list()))
        if item.release_date:
            output += " (" + str(item.release_date)[:4] + ")\n"
        else:
            output += "\n"
        if item.get_all_company_names():
            output += "Published by: " + str(item.get_all_company_names()) + "\n"
        return output

    def item_link(self, item):
        return reverse("file", args=[item.key])


class LatestReviewsFeed(Feed):
    title = "Museum of ZZT - Latest Reviews RSS"
    link = "/reviews/"
    description = "Museum of ZZT review feed"

    def items(self):
        return Review.objects.exclude(zfile_id=None).order_by("-id")[:25]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        output = 'Review by {} covering "{}".'.format(item.get_author(), item.zfile.title)
        if item.rating >= 0:
            output += " ({}/5.0)".format(item.rating)
        return output

    def item_link(self, item):
        return reverse("reviews", args=[item.zfile.filename]) + "#rev-" + str(item.pk)


class LatestUploadsFeed(Feed):
    title = "Museum of ZZT - Latest Uploaded Files RSS"
    link = "/files/"
    description = "Museum of ZZT file upload feed"

    def items(self):
        return File.objects.unpublished().order_by("-id")[:25]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        output = "{} by {}".format(item.title, ", ".join(item.author_list()))
        if item.release_date:
            output += " (" + str(item.release_date)[:4] + ")\n"
        else:
            output += "\n"
        if item.get_all_company_names():
            output += "Published by: " + str(item.get_all_company_names()) + "\n"
        return output

    def item_link(self, item):
        return reverse("file", args=[item.filename])

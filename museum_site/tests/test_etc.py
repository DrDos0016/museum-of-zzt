from datetime import date, datetime

from django.conf import settings
from django.test import TestCase

from museum_site.models import *
from museum_site.core.transforms import *


class Article_Queryset_Test(TestCase):
    @classmethod
    def setUpTestData(self):
        # Create Test Articles
        Article.objects.create(title="Test Article 1", author="Dr. Dos", published=Article.PUBLISHED, spotlight=False, category="Interview")
        Article.objects.create(title="Test Article 2", author="Fishfood", published=Article.UPCOMING, category="Let's Play")
        Article.objects.create(title="Test Article 3", author="Hercules/Hydra", published=Article.UNPUBLISHED, category="Help")
        Article.objects.create(title="Removed Article", author="Big Jerkface", published=Article.REMOVED, category="Publication Pack")
        Article.objects.create(title="Amazing Article", author="Bob", published=Article.PUBLISHED, category="Closer Look")
        Article.objects.create(title="Test Pub Pack A", author="Dr. Dos", published=Article.PUBLISHED, category="Publication Pack")
        Article.objects.create(title="Test Article 4", author="Dr. Dos", published=Article.PUBLISHED, category="Historical")
        Article.objects.create(title="Test Pub Pack B", author="Dr. Dos", published=Article.PUBLISHED, category="Publication Pack")

    def test_qs_manual_order(self):
        qs = Article.objects.all().order_by("id")
        answer = [1, 3, 5, 7, 2, 4, 6, 8]
        ordered = qs_manual_order(qs, answer)
        pks = []
        for a in ordered:
            pks.append(a.pk)
        self.assertEqual(pks, answer)

    def test_qs_manual_order_by_string(self):
        qs = Article.objects.all().order_by("id")
        answer = ["Dr. Dos", "Dr. Dos", "Dr. Dos", "Dr. Dos", "Big Jerkface", "Bob", "Fishfood", "Hercules/Hydra"]
        ordered = qs_manual_order(qs, answer, field="author", kind="str")
        authors = []
        for a in ordered:
            authors.append(a.author)
        self.assertEqual(authors, answer)

    def test_qs_to_links(self):
        qs = Article.objects.filter(pk__lt=3).order_by("id")
        results = qs_to_links(qs)
        answer ="<a href=''></a>, <a href=''></a>"
        self.assertEqual(results, answer)


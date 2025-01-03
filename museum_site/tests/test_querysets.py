from datetime import date, datetime

from django.test import TestCase

from museum_site.core.detail_identifiers import *
from museum_site.core.zeta_identifiers import *
from museum_site.models import *


class Article_Queryset_Test(TestCase):
    def setUp(self):
        # Create Test Articles
        Article.objects.create(title="Test Article 1", author="Dr. Dos", published=Article.PUBLISHED, spotlight=False, category="Interview")
        Article.objects.create(title="Test Article 2", author="Fishfood", published=Article.UPCOMING, category="Let's Play")
        Article.objects.create(title="Test Article 3", author="Hercules/Hydra", published=Article.UNPUBLISHED, category="Help")
        Article.objects.create(title="Removed Article", author="Big Jerkface", published=Article.REMOVED, category="Publication Pack")
        Article.objects.create(title="Amazing Article", author="Bob", published=Article.PUBLISHED, category="Closer Look")
        Article.objects.create(title="Test Pub Pack A", author="Dr. Dos", published=Article.PUBLISHED, category="Publication Pack")
        Article.objects.create(title="Test Article 4", author="Dr. Dos", published=Article.PUBLISHED, category="Historical")
        Article.objects.create(title="Test Pub Pack B", author="Dr. Dos", published=Article.PUBLISHED, category="Publication Pack")

    def test_query_credited_authors(self):
        qs = Article.objects.credited_authors().order_by("id")[:3]
        results = []
        for a in qs:
            results.append(a.author)

        answer = ["Dr. Dos", "Fishfood", "Hercules/Hydra"]
        self.assertEqual(results, answer)

    def test_query_in_early_access(self):
        qs = Article.objects.in_early_access().order_by("id")[:3]

        results = []
        for a in qs:
            results.append(a.title)

        answer = ["Test Article 2", "Test Article 3"]
        self.assertEqual(results, answer)

    def test_published(self):
        qs = Article.objects.published().order_by("id")[:3]

        results = []
        for a in qs:
            results.append(a.title)

        answer = ["Test Article 1", "Amazing Article", "Test Pub Pack A"]
        self.assertEqual(results, answer)

    def test_upcoming(self):
        qs = Article.objects.upcoming().order_by("id")

        results = []
        for a in qs:
            results.append(a.title)

        answer = ["Test Article 2"]
        self.assertEqual(results, answer)

    def test_unpublished(self):
        qs = Article.objects.unpublished().order_by("id")

        results = []
        for a in qs:
            results.append(a.title)

        answer = ["Test Article 3"]
        self.assertEqual(results, answer)

    def test_removed(self):
        qs = Article.objects.removed().order_by("id")

        results = []
        for a in qs:
            results.append(a.title)

        answer = ["Removed Article"]
        self.assertEqual(results, answer)

    def test_accessible(self):
        qs = Article.objects.accessible().order_by("id")[:5]

        results = []
        for a in qs:
            results.append(a.title)

        answer = ["Test Article 1", "Test Article 2", "Test Article 3", "Amazing Article", "Test Pub Pack A"]
        self.assertEqual(results, answer)

    def test_publication_packs(self):
        qs = Article.objects.publication_packs().order_by("id")

        results = []
        for a in qs:
            results.append(a.title)

        answer = ["Test Pub Pack A", "Test Pub Pack B"]
        self.assertEqual(results, answer)

    def test_spotlight(self):
        qs = Article.objects.spotlight().order_by("id")[:3]

        results = []
        for a in qs:
            results.append(a.title)

        answer = ["Amazing Article", "Test Pub Pack A", "Test Article 4"]
        self.assertEqual(results, answer)

    def test_upcoming_or_unpublished(self):
        qs = Article.objects.upcoming_or_unpublished().order_by("id")[:5]

        results = []
        for a in qs:
            results.append(a.title)
        answer = ["Test Article 2", "Test Article 3"]
        self.assertEqual(results, answer)

    def test_category(self):
        """ Published Only """
        qs = Article.objects.category("Publication Pack")
        results = []
        for a in qs:
            results.append(a.title)
        answer = ["Test Pub Pack A", "Test Pub Pack B"]
        self.assertEqual(results, answer)

    # TODO
    """def test_search(self):"""

class ZFile_Queryset_Test(TestCase):
    fixtures = ["detail.json", "genre.json", "zeta_configs.json"]

    @classmethod
    def setUpTestData(cls):
        # Create Test ZFiles
        zf1 = File.objects.create(title="Adventure", release_date=None, filename="ADV.ZIP", key="adv")
        zf2 = File.objects.create(title="ZZT Future",release_date=date(year=2069, month=4, day=20), filename="zztfuture.zip", key="zztfuture")
        zf3 = File.objects.create(title="Unpublished Future", release_date=date(year=2069, month=12, day=25), filename="unpub-fut.zip", key="unpub-fut")
        zf4 = File.objects.create(title="The Next One", release_date=date(year=1997, month=3, day=14), filename="next1.zip", key="next1")
        zf5 = File.objects.create(title="MISSINGNO.", filename="lost4evr.zip", key="lost4evr")

        # Add details
        zf3.details.add(DETAIL_UPLOADED)
        zf1.details.add(DETAIL_NEW_FIND)
        zf4.details.add(DETAIL_NEW_FIND)
        zf5.details.add(DETAIL_LOST)

    def test_new_releases(self):
        qs = File.objects.filter(pk__lte=4).new_releases()  # Preserve ordering

        results = []
        for zf in qs:
            results.append((zf.title, str(zf.release_date)))
        answer = [("ZZT Future", "2069-04-20"), ("The Next One", "1997-03-14"), ("Adventure", "None")]
        self.assertEqual(results, answer)

    def test_new_finds(self):
        qs = File.objects.filter(pk__lte=4).new_finds()  # Preserve ordering

        results = []
        for zf in qs:
            results.append(zf.title)
        answer = ["The Next One", "Adventure"]
        self.assertEqual(results, answer)


    def test_published(self):
        qs = File.objects.filter(pk__lte=5).published().order_by("id")

        results = []
        for zf in qs:
            results.append(zf.title)
        answer = ["Adventure", "ZZT Future", "The Next One"]
        self.assertEqual(results, answer)

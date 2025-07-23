from datetime import date, datetime, UTC

from django.test import TestCase

from museum_site.models import Article


class Article_Function_Test(TestCase):
    test_objects_created = False

    @classmethod
    def setUpTestData(self):
        if self.test_objects_created:
            return

        Article.objects.create(
            title="Test Article", author="Test Author", publish_date=datetime(year=2022, month=2, day=28, timezone=UTC), static_directory="test-article",
            published=Article.PUBLISHED,
            category="Closer Look",
        )
        Article.objects.create(
            title="Test Article Unknown Date", author="Test Author/Another Author/Third Author", static_directory="test-article-unknown-date",
            published=Article.PUBLISHED,
            category="Let's Play",
        )
        Article.objects.create(
            title="Test Upcoming Article", author="Test Author", published=Article.UPCOMING,
            category="Misc",
        )
        Article.objects.create(
            title="Test Unpublished Article", author="Test Author", published=Article.UNPUBLISHED
        )
        Article.objects.create(
            title="Test Removed Article 5", author="Test Author/Test Author 2", published=Article.REMOVED, description="My article's summary",
            publish_date=datetime(year=1999, month=12, day=25, timezone=UTC), static_directory="test-removed-article-5",
            category="Let's Play",
        )
        Article.objects.create(
            title="Test Article 6", author="Test Author", publish_date=datetime(year=2004, month=5, day=2, timezone=UTC), category="Closer Look", description="My desc"
        )
        self.test_objects_created = True

    def test_str(self):
        test_article = Article.objects.get(title="Test Article")
        self.assertEqual(str(test_article), "[1] Test Article by Test Author")

    def test_url(self):
        test_article = Article.objects.get(title="Test Article")
        self.assertEqual(test_article.get_absolute_url(), "/article/view/1/test-article/")

    def test_preview_url(self):
        test_article = Article.objects.get(title="Test Article")
        self.assertEqual(test_article.preview_url(), "articles/2022/test-article/preview.png")

    def test_path(self):
        test_article = Article.objects.get(title="Test Article")
        test_article_2 = Article.objects.get(title="Test Article Unknown Date")

        self.assertEqual(test_article.path(), "articles/2022/test-article/")
        self.assertEqual(test_article_2.path(), "articles/unk/test-article-unknown-date/")

    def test_render(self):  # TODO
        self.assertEqual(1, 1)

    def test_render_footnotes(self):  # TODO
        self.assertEqual(1, 1)

    def test_series_links(self):  # TODO
        self.assertEqual(1, 1)

    def test_series_range(self):  # TODO
        self.assertEqual(1, 1)

    def test_early_access_price(self):
        qs = Article.objects.filter(pk__lte=5).order_by("pk")
        idx = 0
        answers = ["???", "???", "$2.00 USD", "$5.00 USD", "???"]
        for a in qs:
            self.assertEqual(a.early_access_price, answers[idx])
            idx += 1

    def test_init_access_level(self):  # TODO
        self.assertEqual(1, 1)

    def test_init_icons(self):  # TODO
        self.assertEqual(1, 1)

    def test_export_urls(self):  # TODO
        self.assertEqual(1, 1)

    def test_word_count(self):  # TODO
        self.assertEqual(1, 1)

    def test_category_slug(self):
        qs = Article.objects.filter(pk__lte=3).order_by("pk")
        idx = 0
        answers = ["closer-look", "lets-play", "misc"]
        for a in qs:
            self.assertEqual(a.category_slug(), answers[idx])
            idx += 1

    def test_get_meta_tag_context(self):
        a = Article.objects.get(pk=5)
        answer = {
            "author": ["name", "Test Author, Test Author 2"],
            "description": ["name", "My article's summary"],
            "og:title": ["property", "Test Removed Article 5 - Museum of ZZT"],
            "og:image": ["property", "articles/1999/test-removed-article-5/preview.png"]
        }
        self.assertEqual(a.get_meta_tag_context(), answer)

    def test_get_field_view(self):  # TODO
        self.assertEqual(1, 1)

    def test_get_field_authors(self):
        qs = Article.objects.filter(pk__lte=2).order_by("pk")
        idx = 0
        answers = [
            {"label": "Author", "value": "Test Author"},
            {"label": "Authors", "value": "Test Author, Another Author, Third Author"},
        ]
        for a in qs:
            self.assertEqual(a.get_field_authors(), answers[idx])
            idx += 1

    def test_get_field_article_date(self):
        qs = Article.objects.filter(pk__lte=2).order_by("pk")
        idx = 0
        answers = [
            {"label": "Publish Date", "value": "Feb 28, 2022", "safe": True},
            {"label": "Publish Date", "value": "<i>- Unknown Date - </i>", "safe": True}
        ]
        for a in qs:
            self.assertEqual(a.get_field_article_date(), answers[idx])
            idx += 1

    def test_get_field_category(self):
        a = Article.objects.get(pk=2)
        self.assertEqual(a.get_field_category(), {"label": "Category", "value": "Let's Play"})

    def test_get_field_series(self):  # TODO
        self.assertEqual(1, 1)

    def test_get_field_description(self):
        a = Article.objects.get(pk=5)
        self.assertEqual(a.get_field_description(), {"label": "Description", "value": "My article's summary"})

    def test_get_field_associated_zfiles(self):  # TODO
        self.assertEqual(1, 1)

    def test_get_context_detailed(self):  # TODO -- This doesn't cover enough. Needs related data
        a = Article.objects.get(pk=6)
        context = a.context_detailed()
        column = [
            {"label": "Author", "value": "Test Author"},
            {"label": "Publish Date", "value": "May 02, 2004", "safe": True},
            {"label": "Category", "value": "Closer Look"},
            {"label": "Associated Files", "value": "<i>None</i>", "safe": True},
            {"label": "Description", "value": "My desc"},
        ]
        self.assertEqual(context["roles"], ["model-block", "detailed"])
        self.assertEqual(context["columns"][0], column)

    def test_get_context_list(self):
        a = Article.objects.get(pk=6)
        context = a.context_list()
        cells = [
            {"value": "<a href='/article/view/6/test-article-6/'>Test Article 6</a>", "safe": True},
            {"label": "Author", "value": "Test Author"},
            {"label": "Publish Date", "value": "May 02, 2004", "safe": True},
            {"label": "Category", "value": "Closer Look"},
            {"label": "Description", "value": "My desc"}
        ]
        self.assertEqual(context["roles"], ["list"])
        self.assertEqual(context["cells"], cells)

    def test_get_context_gallery(self):
        a = Article.objects.get(pk=6)
        context = a.context_gallery()
        fields = [
            {"label": "Author", "value": "Test Author"}
        ]
        self.assertEqual(context["roles"], ["model-block", "gallery"])
        self.assertEqual(context["fields"], fields)

    def test_get_guideword_author(self):
        a = Article.objects.get(pk=5)
        self.assertEqual(a.get_guideword_author(), "Test Author/Test Author 2")

    def test_get_guideword_category(self):
        a = Article.objects.get(pk=5)
        self.assertEqual(a.get_guideword_category(), "Let's Play")

    def test_get_guideword_date(self):
        a = Article.objects.get(pk=5)
        self.assertEqual(a.get_guideword_date(), "Dec 25, 1999")

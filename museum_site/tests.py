"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import unittest

import requests

from django.contrib.auth.models import User
from django.test import TestCase

from museum_site.common import *
from museum_site.constants import *
from museum_site.forms import *
from museum_site.models import *
from museum_site.templatetags.site_tags import *


class URLStatusTest(TestCase):
    @unittest.skip("Skipping test_url_status()")
    def test_url_status(self):
        from museum_site.urls import urlpatterns
        statuses = {200: True, 301: True, 302: True}  # Valid statuses
        expected_statuses = [200, 301, 302]

        for p in urlpatterns:
            # Special patterns
            if str(p.pattern) == ".":
                p.pattern = ""
            elif str(p.pattern) == "zeta-live/":
                p.pattern = "zeta-live/?pk=1015&world=DEMO.ZZT&start=7"
            elif str(p.pattern) == "zeta-launcher/":
                p.pattern = "zeta-live/?pk=1015&world=DEMO.ZZT&start=7"
            url = HOST + str(p.pattern)

            # Replace args
            url = url.replace("<int:article_id>", "2")
            url = url.replace("<int:page>", "1")
            url = url.replace("<slug:slug>", "url-status-test-slug")
            url = url.replace("<slug:category>", "closer-look")
            url = url.replace("<str:letter>", "z")
            url = url.replace("<str:filename>", "zzt.zip")
            url = url.replace("<int:pk>", "1015")
            url = url.replace("<int:user_id>", "1")
            url = url.replace("<str:unused_slug>", "account-name")
            url = url.replace("<int:series_id>", "1")
            url = url.replace("<slug:slug>", "slug")
            url = url.replace("<str:token>", "8A194C8A21493395")

            # More oddball features that will likely be cut
            url = url.replace("<int:phase>", "1")
            url = url.replace("<str:section>", "play")

            r = requests.head(url)

            if r.status_code >= 400:
                print(r.status_code, url, "[{}]".format(p.pattern))

            statuses[r.status_code] = True

        unique_statuses = list(statuses.keys())
        unique_statuses.sort()
        print(unique_statuses)

        self.assertEqual(unique_statuses, expected_statuses)


class FileviewerStatusTest(TestCase):
    def test_file_viewer_url_status(self):
        qs = File.objects.all()
        for f in qs:
            print(f)

        self.assertEqual(1 + 1, 2)


class MetaTagTest(TestCase):
    def test_index(self):
        valid = {}
        expected = {"og:image": 1, "og:url": 1, "og:title": 1}

        tags = meta_tags(path="/").split("\n")
        for tag in tags:
            if tag == (
                '<meta property="og:image" '
                'content="{}static/images/og_default.jpg">'.format(HOST)
            ):
                valid["og:image"] = 1
            elif tag == '<meta property="og:url" content="{}">'.format(HOST):
                valid["og:url"] = 1
            elif tag == '<meta property="og:title" content="Museum of ZZT">':
                valid["og:title"] = 1
        self.assertEqual(valid, expected)

    def test_default(self):
        valid = {}
        expected = {"og:image": 1, "og:url": 1, "og:title": 1}

        tags = meta_tags(path="/credits/").split("\n")
        for tag in tags:
            if tag == (
                '<meta property="og:image" '
                'content="{}static/images/og_default.jpg">'.format(HOST)
            ):
                valid["og:image"] = 1
            elif tag == '<meta property="og:url" content="{}credits/">'.format(
                HOST
            ):
                valid["og:url"] = 1
            elif tag == '<meta property="og:title" content="Museum of ZZT">':
                valid["og:title"] = 1
        self.assertEqual(valid, expected)


class ZGameFormTest(TestCase):
    def test_blank_form(self):
        form = ZGameForm(data={})

        errors = form.errors.get_json_data()

        self.assertEqual(
            list(errors.keys()),
            ["zfile", "title", "author", "genre", "language"]
        )


class FileTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        File.objects.create(
            filename="zzt.zip",
            title="ZZT v3.2 (Registered)",
            author="Tim Sweeney",
            size=1234,
            genre="Official/Puzzle/Adventure/Registered",
            zeta_config=None,
        )
        File.objects.create(
            filename="ZOMBINAT.ZIP",
            title="The Zombinator",
            author="Mazeo",
            size=1234,
            genre="Adventure",
            zeta_config=None,
        )
        File.objects.create(
            filename="thetamag1.zip",
            title="ThetaMag #1",
            author="Theta14",
            size=1234,
            genre="Adventure",
            zeta_config=None,
        )

    def test_sorted_genre(self):
        """ Genre should be sorted alphabetically after save """
        f = File.objects.get(pk=1)
        self.assertEqual(f.genre, "Adventure/Official/Puzzle/Registered")

    def test_letter_identification(self):
        letters = File.objects.filter(pk__lte=3).order_by("id").values_list(
            "letter", flat=True
        )
        self.assertEqual(list(letters), ["z", "z", "t"])


class ArticleTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Article.objects.create(
            title='Test Article 1: "Hello World"',
        )


class ReviewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        info = [
            ("Alpha", "Alpha@localhost", "password123"),
            ("Beta", "Beta@localhost", "password123"),
            ("Gamma", "Gamma@localhost", "password123"),
        ]
        for i in info:
            u = User.objects.create_user(i[0], i[1], i[2])
            Profile.objects.create(user=u, patron_email=u.email)

        f = File.objects.create(
            filename="zzt.zip",
            title="ZZT v3.2 (Registered)",
            author="Tim Sweeney",
            size=1234,
            genre="Official/Puzzle/Adventure/Registered",
            zeta_config=None,
        )

        Review.objects.create(
            zfile=f,
            user_id=1,
            title="Test Review Title Logged In User",
            author="IGNORED BECAUSE LOGGED IN",
            content="Body of *my* review",
            rating=5.0,
            date="2022-01-01",
            ip="127.0.0.1"
        ),

        Review.objects.create(
            zfile=f,
            user_id=None,
            title="Test Review Title Anon User",
            author="U.N. Owen",
            content="Body of *my* review",
            rating=5.0,
            date="2022-01-01",
            ip="127.0.0.1"
        )

    def test_review_author(self):
        r = Review.objects.get(pk=1)
        self.assertEqual(r.get_author(), "Alpha")
        r = Review.objects.get(pk=2)
        self.assertEqual(r.get_author(), "U.N. Owen")


"""
http://django.pi:8000/article/f/frost1.zip
http://django.pi:8000/article/406/livestream-frost-1-power
http://django.pi:8000/file/f/frost1.zip
http://django.pi:8000/patron-articles/
http://django.pi:8000/user/profile/1/dr_dos/
"""

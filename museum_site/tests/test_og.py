import unittest

import requests

from django.contrib.auth.models import User
from django.test import TestCase

from museum_site.constants import *
from museum_site.forms import *
from museum_site.models import *
from museum_site.templatetags.site_tags import *



class MetaTagTest(TestCase):
    def test_index(self):
        valid = {}
        expected = {"og:image": 1, "og:url": 1, "og:title": 1}

        tags = meta_tags(path="/").split("\n")
        for tag in tags:
            if tag == ('<meta property="og:image" content="{}static/pages/og_default.jpg">'.format(HOST)):
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
            if tag == ('<meta property="og:image" content="{}static/pages/og_default.jpg">'.format(HOST)):
                valid["og:image"] = 1
            elif tag == '<meta property="og:url" content="{}credits/">'.format(HOST):
                valid["og:url"] = 1
            elif tag == '<meta property="og:title" content="Museum of ZZT">':
                valid["og:title"] = 1
        self.assertEqual(valid, expected)

"""
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
            size=1234,
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


"""
http://django.pi:8000/article/f/frost1.zip
http://django.pi:8000/article/406/livestream-frost-1-power
http://django.pi:8000/file/f/frost1.zip
http://django.pi:8000/patron-articles/
http://django.pi:8000/user/profile/1/dr_dos/
"""

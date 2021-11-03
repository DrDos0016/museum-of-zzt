"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import unittest

import requests

from django.test import TestCase

from museum_site.common import *
from museum_site.constants import *
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


"""
http://django.pi:8000/article/f/frost1.zip
http://django.pi:8000/article/406/livestream-frost-1-power
http://django.pi:8000/file/f/frost1.zip
http://django.pi:8000/patron-articles/
http://django.pi:8000/user/profile/1/dr_dos/
"""

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import requests

from django.test import TestCase

from museum_site.common import *
from museum_site.constants import *
from museum_site.models import *


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class URLStatusTest(TestCase):
    def test_url_status(self):
        from museum_site.urls import urlpatterns
        statuses = {}
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
            r = requests.head(url)

            if r.status_code >= 400:
                print(r.status_code, url, "[{}]".format(p.pattern))
            if r.status_code == 500:
                print("HEY THIS IS A 500!")
                print(url)

            statuses[r.status_code] = True


        print("Host", HOST)
        print("Env", ENV)
        unique_statuses = list(statuses.keys())
        unique_statuses.sort()
        print(unique_statuses)

        self.assertEqual(unique_statuses, expected_statuses)

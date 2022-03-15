import unittest

from django.test import TestCase
from django.test import Client

from museum_site.models import *

c = Client()

class URLTest(unittest.TestCase):
    def test_old_zfile_urls(self):
        """ Ensure old URLs properly redirect """
        urls = [
            "/file/a/oaktown1.zip",
            "/file/a/oaktown1.zip/",
            "/play/a/oaktown1.zip/",
            "/review/a/oaktown1.zip/",
            "/file/a/aura%202004-11-13.zip",
            "/file/a/aura%202004-11-13.zip/",
            "/file/a/aura%202004-11-13.zip/?file=oldAURA.ZZT&board=25",
            "/file/t/tweird.zip/?file=TWEIRD.ZZT&board=24",
            "/play/t/tweird.zip/",
            "/attributes/a/aura 2004-11-13.zip/",
            "/play/a/aura 2004-11-13.zip/?player=zeta&mode=popout&scale=1",
            "/play/a/aura 2004-11-13.zip/?player=zeta&mode=popout&scale=1&live=1&world=oldAURA.ZZT&start=36",
            "/article/m/merbotia.zip/",
        ]
        results = []
        answers = [
            (301, "/file/a/oaktown1.zip/"),
            (302, "/file/a/oaktown1/"),
            (302, "/play/a/oaktown1/"),
            (302, "/review/a/oaktown1/"),
            (301, "/file/a/aura%202004-11-13.zip/"),
            (302, "/file/a/aura%202004-11-13/"),
            (302, "/file/a/aura%202004-11-13/?file=oldAURA.ZZT&board=25"),
            (302, "/file/t/tweird/?file=TWEIRD.ZZT&board=24"),
            (302, "/play/t/tweird/"),
            (302, "/attributes/a/aura%202004-11-13/"),
            (302, "/play/a/aura%202004-11-13/?player=zeta&mode=popout&scale=1"),
            (302, "/play/a/aura%202004-11-13/?player=zeta&mode=popout&scale=1&live=1&world=oldAURA.ZZT&start=36"),
            (302, "/article/m/merbotia/"),
        ]

        for url in urls:
            r = c.get(url)
            results.append((r.status_code, r.url))

        self.assertEqual(results, answers)

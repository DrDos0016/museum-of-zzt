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

    def test_legacy_redirects(self):
        """ Ensure old URLs properly redirect """
        urls = [
            "/article/categories/",
            "/article/help/",
            "/article/194/page/2/closer-look-turmoil/",
            "/article/194/closer-look-turmoil/",
            "/detail/zzt-save/",
            "/zzt-worlds/",
            "/super-zzt/",
            "/utilities/",
            "/zzm-audio/",
            "/zig-worlds/",
            "/modified-gfx/",
            "/modified-exe/",
            "/ms-dos/",
            "/lost-worlds/",
            "/uploaded/",
            "/featured/",
            # Article URLs
            "/closer-looks/",
            "/livestreams/",
            # Policy URLs
            "/data-integrity/",
        ]

        results = []
        answers = [
            (301, "/article/category/"),
            (301, "/article/category/help/"),
            (301, "/article/view/194/page/2/closer-look-turmoil/"),
            (301, "/article/view/194/closer-look-turmoil/"),
            (301, "/detail/view/zzt-save/"),
            (301, "/detail/view/zzt-world/"),
            (301, "/detail/view/super-zzt-world/"),
            (301, "/detail/view/utility/"),
            (301, "/detail/view/zzm-audio/"),
            (301, "/detail/view/zig-world/"),
            (301, "/detail/view/modified-graphics/"),
            (301, "/detail/view/modified-executable/"),
            (301, "/detail/view/ms-dos/"),
            (301, "/detail/view/lost-world/"),
            (301, "/detail/view/uploaded/"),
            (301, "/detail/view/featured-world/"),
            (301, "/article/category/closer-look/"),
            (301, "/article/category/livestream/"),
            (301, "/policy/data-integrity/"),
        ]

        for url in urls:
            r = c.get(url)
            results.append((r.status_code, r.url))
        self.assertEqual(results,answers)

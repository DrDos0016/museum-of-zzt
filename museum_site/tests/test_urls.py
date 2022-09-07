import unittest

from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from django.urls import reverse

from museum_site.models import *
from museum_site.urls import urlpatterns

c = Client()
c.login(username="teststaff", password="testpassword")


class URLTest(unittest.TestCase):
    #def setUp(self):
    #    user = User.objects.create_user("teststaff", "teststaff@localhost", "testpassword")

    def test_old_zfile_urls(self):
        """ Ensure old ZFile URLs properly redirect """
        urls = [
            "/file/a/oaktown1.zip",
            "/file/a/oaktown1.zip/",
            "/file/view/oaktown1.zip/",
            "/play/a/oaktown1.zip/",
            "/file/play/oaktown1.zip/",
            "/review/a/oaktown1.zip/",
            "/file/a/aura%202004-11-13.zip",
            "/file/a/aura%202004-11-13.zip/",
            "/file/a/aura%202004-11-13.zip/?file=oldAURA.ZZT&board=25",
            "/file/view/aura%202004-11-13.zip/?file=oldAURA.ZZT&board=25",
            "/file/t/tweird.zip/?file=TWEIRD.ZZT&board=24",
            "/play/t/tweird.zip/",
            "/attributes/a/aura 2004-11-13.zip/",
            "/play/a/aura 2004-11-13.zip/?player=zeta&mode=popout&scale=1",
            "/play/a/aura 2004-11-13.zip/?player=zeta&mode=popout&scale=1&live=1&world=oldAURA.ZZT&start=36",
            "/file/play/aura%202004-11-13.zip/?player=zeta&mode=popout&scale=1&live=1&world=oldAURA.ZZT&start=36",
            "/article/m/merbotia.zip/",
        ]
        results = []
        answers = [
            (301, "/file/a/oaktown1.zip/"),  # Which then continues redirecting...
            (301, "/file/view/oaktown1.zip/"),
            (302, "/file/view/oaktown1/"),
            (301, "/file/play/oaktown1.zip/"),
            (302, "/file/play/oaktown1/"),
            (301, "/file/review/oaktown1.zip/"),
            (301, "/file/a/aura%202004-11-13.zip/"),
            (301, "/file/view/aura%202004-11-13.zip/"),
            (301, "/file/view/aura%202004-11-13.zip/?file=oldAURA.ZZT&board=25"),
            (302, "/file/view/aura%202004-11-13/?file=oldAURA.ZZT&board=25"),
            (301, "/file/view/tweird.zip/?file=TWEIRD.ZZT&board=24"),
            (301, "/file/play/tweird.zip/"),
            (301, "/file/attribute/aura%202004-11-13.zip/"),
            (301, "/file/play/aura%202004-11-13.zip/?player=zeta&mode=popout&scale=1"),
            (301, "/file/play/aura%202004-11-13.zip/?player=zeta&mode=popout&scale=1&live=1&world=oldAURA.ZZT&start=36"),
            (302, "/file/play/aura%202004-11-13/?player=zeta&mode=popout&scale=1&live=1&world=oldAURA.ZZT&start=36"),
            (301, "/file/article/merbotia.zip/"),
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
            # File URLs
            "/roulette/?seed=1653414763",
            "/search/",
            "/advanced-search/",
            "/mass-downloads/",
            "/article/f/frost1/",
            "/attributes/m/merbotia/",
            "/download/o/on_a_distant_moon/",
            "/file/local/",
            "/file/m/merc/",
            "/pk/420/",
            "/play/e/endofwor/",
            "/review/l/lostmonk/",
            "/browse/",
            "/browse/o/",
            "/new/",
            "/new-releases/",
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
            (301, "/file/roulette/?seed=1653414763"),
            (301, "/file/search/"),
            (301, "/file/advanced-search/"),
            (301, "/file/mass-downloads/"),
            (301, "/file/article/frost1/"),
            (301, "/file/attribute/merbotia/"),
            (301, "/file/download/on_a_distant_moon/"),
            (301, "/file/view-local/"),
            (301, "/file/view/merc/"),
            (301, "/file/pk/420/"),
            (301, "/file/play/endofwor/"),
            (301, "/file/review/lostmonk/"),
            (301, "/file/browse/"),
            (301, "/file/browse/o/"),
            (301, "/file/browse/new-releases/"),
            (301, "/file/browse/new-releases/"),
        ]

        for url in urls:
            r = c.get(url)
            results.append((r.status_code, r.url))
        self.assertEqual(results, answers)

    def test_current_urls_without_args(self):
        """ Test all non-legacy redirect urls and url patterns with arguments return 200 status """
        for url in urlpatterns:
            fh.write(str(url.pattern) + "\n")
            # Ignore legacy redirects
            if "legacy_redirect" in str(url.callback):
                continue
            if "<" in str(url.pattern):
                continue
            if url.name is None or url.name in ["patreon"]:
                continue

            r = c.get(reverse(url.name), follow=True)

            if r.status_code != 200:
                print("{}: {}".format(r.status_code, url.pattern))
            self.assertEqual(r.status_code, 200)

    """
    def test_current_urls_with_args(self):
        #"" Test all non-legacy redirect url patterns with arguments return 200 status ""
        test_urls = {
            "article/category/<slug:category_slug>/": "article/category/closer-look/",
            "article/view/<int:article_id>/page/<int:page>/<slug:slug>/": "article/view/166/page/2/closer-look-dungeons-of-zzt/",
            "article/view/<int:article_id>/<slug:slug>/": "article/view/166/closer-look-dungeons-of-zzt/",
            #"collection/manage-contents/": "article/view/166/closer-look-dungeons-of-zzt/",
        }
        for url in urlpatterns:
            # Ignore legacy redirects
            if "legacy_redirect" in str(url.callback):
                continue
            if "<" not in str(url.pattern):
                continue

            r = c.get("/" + test_urls.get(str(url.pattern), "XYZZY"), follow=True)
            if r.status_code != 200:
                print("{}: {}".format(r.status_code, url.pattern))
            self.assertEqual(r.status_code, 200)
    """

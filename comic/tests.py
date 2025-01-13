from datetime import date, datetime, timezone

from django.test import TestCase

from comic.models import Comic


class Comic_Test(TestCase):
    @classmethod
    def setUpTestData(self):
        Comic.objects.create(title="Test Comic Lemmy", comic_id=100, comic_account="lemmy", date=date.fromisoformat("2002-04-05"), commentary="Test commentary", transcript="Test")
        Comic.objects.create(title="Test Comic Bencomic", comic_id=101, comic_account="bencomic", date=date.today(), commentary="Test commentary", transcript="Test")
        Comic.objects.create(title="Test Comic Kaddar", comic_id=102, comic_account="kaddar", date=date.today(), commentary="Test commentary", transcript="Test")
        Comic.objects.create(title="Test Comic Shapiro", comic_id=103, comic_account="mr-shapiro", date=date.today(), commentary="Test commentary", transcript="Test")
        Comic.objects.create(title="Test Comic Revvy", comic_id=104, comic_account="revvy", date=date.today(), commentary="Test commentary", transcript="Test")
        Comic.objects.create(title="Test Comic Frost", comic_id=105, comic_account="frost", date=date.fromisoformat("2006-09-25"), commentary="Test commentary", transcript="Test")

    def test_str(self):
        test_object = Comic.objects.get(title="Test Comic Lemmy")
        self.assertEqual(str(test_object), "[1] 100 - Test Comic Lemmy")

    def test_image_url(self):
        test_qs = list(Comic.objects.filter(comic_id__lte=105).order_by("comic_id"))
        self.assertEqual(test_qs[0].image_url(), "comic/lemmy/lemmy20020405.jpg")
        self.assertEqual(test_qs[1].image_url(), "")
        self.assertEqual(test_qs[2].image_url(), "comic/kaddar/zztkadcomix102.gif")
        self.assertEqual(test_qs[3].image_url(), "comic/mr-shapiro/shapiro-103.gif")
        self.assertEqual(test_qs[4].image_url(), "comic/revvy/revvy104.gif")
        self.assertEqual(test_qs[5].image_url(), "comic/frost/2006-09-25.png")

    def test_sc_url(self):
        test_object = Comic.objects.get(title="Test Comic Bencomic")
        self.assertEqual(test_object.sc_url(), "http://www.stripcreator.com/comics/bencomic/101")


    def test_count(self):
        count = Comic.objects.all().count()
        self.assertEqual(count, 6)

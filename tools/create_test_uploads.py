import os
import shutil
import sys

import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import File, Detail


def main():
    to_make = int(input("Number of test uploads to create: "))
    for x in range(0, to_make):
        num = str(x + 1)
        fname = "test{}.zip".format(num)
        shutil.copyfile("/var/projects/museum/zgames/z/zzt.zip", "/var/projects/museum/zgames/uploaded/" + fname)
        f = File(letter="T", filename=fname, title=("Test Upload" + num), author="Musuem Test", size="69", genre="Action/Adventure", release_date="2018-04-20", company="Museum Productions")
        f.save(new_upload=True)
        f.details.add(Detail.objects.get(pk=18)) # TODO: Unhardcode #
        print("Uploaded " + fname)

    return True

if __name__ == "__main__":
    main()


"""
    letter = models.CharField(max_length=1, db_index=True)
    filename = models.CharField(max_length=50)
    title = models.CharField(max_length=80)
    sort_title = models.CharField(
        max_length=100, db_index=True, default="", blank=True,
        help_text="Leave blank to set automatically"
    )
    author = models.CharField(max_length=80)
    size = models.IntegerField(default=0)
    genre = models.CharField(max_length=80, blank=True, default="")
    release_date = models.DateField(default=None, null=True, blank=True)
    release_source = models.CharField(
        max_length=20, null=True, default=None, blank=True
    )
    screenshot = models.CharField(
        max_length=80, blank=True, null=True, default=None
    )
    company = models.CharField(
        max_length=80, default="", blank=True, null=True
    )
    description = models.TextField(null=True, blank=True, default="")
    review_count = models.IntegerField(
        default=0, help_text="Set automatically. Do not adjust."
    )
    rating = models.FloatField(null=True, default=None, blank=True)
    details = models.ManyToManyField("Detail", default=None, blank=True)
    articles = models.ManyToManyField("Article", default=None, blank=True,
                                      limit_choices_to={'page': 1})
    article_count = models.IntegerField(
        default=0, help_text="Set automatically. Do not adjust."
    )
    checksum = models.CharField(max_length=32, null=True,
                                blank=True, default="")
    superceded = models.ForeignKey("File", db_column="superceded_id",
                                   null=True, blank=True, default=None)
    playable_boards = models.IntegerField(null=True, blank=True, default=None, help_text="Set automatically. Do not adjust.")
    total_boards = models.IntegerField(null=True, blank=True, default=None, help_text="Set automatically. Do not adjust.")
    archive_name = models.CharField(max_length=80, default="", blank=True, help_text="ex: zzt_burgerj")

    aliases = models.ManyToManyField("Alias", default=None, blank=True)
    upload_date = models.DateTimeField(null=True, auto_now_add=True, db_index=True, help_text="Date File was uploaded to the Museum")
    publish_date = models.DateTimeField(null=True, default=None, db_index=True, help_text="Date File was published on the Museum")
    last_modified = models.DateTimeField(auto_now=True, help_text="Date DB entry was last modified")
"""

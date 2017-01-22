
from django.db import models


class Comic(models.Model):
    STRIPCREATOR_ACCOUNTS = (
        ("benco", "Benco"),
        ("bencomic", "Bencomic")
    )
    title = models.CharField(max_length=100)
    stripcreator_id = models.IntegerField()
    stripcreator_account = models.CharField(
        max_length=8, choices=STRIPCREATOR_ACCOUNTS
    )
    date = models.DateField(null=True, blank=True, default=None)
    transcript = models.TextField()
    characters = models.ManyToManyField("Character")

    class Meta:
        ordering = ["stripcreator_id"]

    def __str__(self):
        return ("[" + str(self.id) + "] "
                "{" + str(self.stripcreator_id) + "} " +
                self.title)

    def image_url(self):
        url = "bencomic/comics/{}/{}.png".format(
            self.stripcreator_account,
            self.stripcreator_id
        )
        return url

    def sc_url(self):
        url = "http://www.stripcreator.com/comics/{}/{}".format(
            self.stripcreator_account,
            self.stripcreator_id
        )
        return url


class Character(models.Model):
    name = models.CharField(max_length=25)
    benco_image = models.CharField(max_length=25)
    bencomic_image = models.CharField(max_length=25)

    class Meta:
        ordering = ["name"]

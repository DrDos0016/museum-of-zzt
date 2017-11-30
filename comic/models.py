
from django.db import models


class Comic(models.Model):
    ACCOUNTS = (
        ("benco", "Benco"),
        ("bencomic", "Bencomic"),
        ("lemmy", "Lemmy"),
        ("mr-shapiro", "Mr. Shapiro"),
        ("nomad", "Nomad's ZZT Comics"),
        ("kaddar", "Yellow Boarders"),
        ("frost", "Frost"),
        ("revvy", "The Prophesies of Revvy"),
        ("zamros", "Zamros: The Comic"),
        ("ubgs", "Ol' Uncle Bo's Gamblin' Shack")
    )
    title = models.CharField(max_length=100)
    comic_id = models.IntegerField()
    comic_account = models.CharField(
        max_length=10, choices=ACCOUNTS
    )
    date = models.DateField(null=True, blank=True, default=None)
    commentary = models.TextField(null=True, blank=True, default="")
    transcript = models.TextField(null=True, blank=True, default=None)
    characters = models.ManyToManyField("Character")

    class Meta:
        ordering = ["comic_account", "comic_id"]

    def __str__(self):
        return ("[" + str(self.id) + "] "
                "{" + str(self.comic_id) + "} " +
                self.title)

    def image_url(self):
        if self.comic_account in ["bencomic", "Bencomic"]:
            url = "comic/{}/{}.png".format(
                self.comic_account,
                self.comic_id
            )
        elif self.comic_account == "lemmy":
            url = "comic/lemmy/lemmy{}.jpg".format(
                str(self.date).replace("-", "")
            )
        elif self.comic_account == "kaddar":
            url = "comic/kaddar/zztkadcomix{}.gif".format(
                self.comic_id
            )
        elif self.comic_account == "mr-shapiro":
            url = "comic/mr-shapiro/shapiro-{}.gif".format(
                self.comic_id
            )
        elif self.comic_account in ["nomad", "revvy", "ubgs", "zamros"]:
            url = "comic/{}/{}{}.gif".format(
                self.comic_account,
                self.comic_account,
                self.comic_id
            )
        elif self.comic_account == "frost":
            url = "comic/frost/{}.png".format(
                str(self.date)
            )
        return url

    def sc_url(self):
        url = "http://www.stripcreator.com/comics/{}/{}".format(
            self.comic_account,
            self.comic_id
        )
        return url


class Character(models.Model):
    name = models.CharField(max_length=25)
    benco_image = models.CharField(max_length=25)
    bencomic_image = models.CharField(max_length=25)

    class Meta:
        ordering = ["name"]

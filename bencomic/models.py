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
    date = models.DateField()
    transcript = models.TextField()
    characters = models.ManyToManyField("Character")

    class Meta:
        ordering = ["-date"]


class Character(models.Model):
    name = models.CharField(max_length=25)
    image = models.CharField(max_length=25)

    class Meta:
        ordering = ["name"]

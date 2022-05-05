from django.db import models
from django.template.defaultfilters import slugify

from museum_site.models.base import BaseModel


class Genre(BaseModel):
    model_name = "Genre"
    title = models.CharField(max_length=80)
    description = models.TextField(default="")
    visible = models.BooleanField(default=True)
    slug = models.SlugField(max_length=80, editable=False)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


    def url(self):
        return "/genre/{}/".format(self.slug)


    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Genre, self).save(*args, **kwargs)

from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

from museum_site.models.base import BaseModel
from museum_site.querysets.genre_querysets import *


class Genre(BaseModel):
    objects = Genre_Queryset.as_manager()
    model_name = "Genre"

    title = models.CharField(max_length=80)
    description = models.TextField(default="")
    visible = models.BooleanField(default=True)
    slug = models.SlugField(max_length=80, editable=False)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("browse_field", kwargs={"field":"genre", "value":self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Genre, self).save(*args, **kwargs)

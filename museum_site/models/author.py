from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from museum_site.querysets.author_querysets import *


class Author(models.Model):
    """ Representation of an author associated with a ZFile """
    objects = Author_Queryset.as_manager()
    model_name = "Author"

    title = models.CharField(max_length=120, db_index=True, editable=True, help_text="Author Name")
    slug = models.SlugField(max_length=120, db_index=True, editable=False)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def generate_automatic_slug(self, save=True):
        self.slug = slugify(self.title, allow_unicode=True)
        if self.slug == "":
            self.slug = self.title.lower()
        if save:
            self.save()

    def url(self):
        if not self.slug:
            self.slug = "ERROR"
        return reverse("browse_field", kwargs={"field":"author", "value": self.slug})

    def get_absolute_url(self):
        return reverse("browse_field", kwargs={"field":"author", "value": self.slug})

from django.db import models
from django.template.defaultfilters import slugify

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

    def save(self, *args, **kwargs):
        # Save
        super(Author, self).save(*args, **kwargs)

    def generate_automatic_slug(self, save=True):
        self.slug = slugify(self.title)
        if save:
            self.save()

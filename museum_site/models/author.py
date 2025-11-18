from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from museum_site.querysets.author_querysets import *


class Author(models.Model):
    """ Representation of an author associated with a ZFile """
    objects = Author_Queryset.as_manager()
    model_name = "Author"

    title = models.CharField(max_length=120, db_index=True, help_text="Author Name")
    slug = models.SlugField(max_length=120, db_index=True, help_text="Automatically updated on save unless locked.")
    lock_slug = models.BooleanField(default=False, help_text="Check to disable recalculating slug on save.")

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def admin_url(self):
        name = self.model_name.replace("-", "_").lower()
        return "/admin/museum_site/{}/{}/change/".format(name, self.id)

    def generate_automatic_slug(self, save=True):
        self.slug = slugify(self.title, allow_unicode=True)
        if self.slug == "":
            self.slug = self.title.lower()
        if save:
            self.save()

    def url(self):
        if not self.slug:
            self.slug = "ERROR"
        return reverse("zfile_browse_field", kwargs={"field":"author", "value": self.slug})

    def get_absolute_url(self):
        if not self.slug:
            self.slug = "ERROR"
        return reverse("zfile_browse_field", kwargs={"field":"author", "value": self.slug})

    def save(self, *args, **kwargs):
        if not self.lock_slug:
            self.slug = slugify(self.title)
        super(Author, self).save(*args, **kwargs)

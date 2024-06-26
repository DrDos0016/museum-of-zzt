from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from museum_site.querysets.company_querysets import *


class Company(models.Model):
    """ Representation of a company associated with a ZFile """
    objects = Company_Queryset.as_manager()
    model_name = "Company"

    title = models.CharField(max_length=120, db_index=True, editable=True, help_text="Company Name")
    slug = models.SlugField(max_length=120, db_index=True, editable=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Save
        super(Company, self).save(*args, **kwargs)

    def generate_automatic_slug(self, save=True):
        self.slug = slugify(self.title, allow_unicode=True)
        if self.slug == "":
            self.slug = self.title.lower()

        # Edge cases
        if self.title in ["⌂⌂⌂⌂ ⌂⌂⌂⌂⌂⌂⌂⌂⌂"]:
            self.slug = self.title.lower()

        if save:
            self.save()

    def url(self):
        if not self.slug:
            self.slug = "ERROR"
        return reverse("zfile_browse_field", kwargs={"field":"company", "value": self.slug})

    def get_absolute_url(self):
        if not self.slug:
            self.slug = "ERROR"
        return reverse("zfile_browse_field", kwargs={"field":"company", "value": self.slug})

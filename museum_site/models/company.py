from django.db import models
from django.template.defaultfilters import slugify


class Company(models.Model):
    """ Representation of a company associated with a ZFile """
    model_name = "Company"

    title = models.CharField(max_length=120, db_index=True, editable=True, help_text="Company Name")
    slug = models.SlugField(max_length=120, db_index=True, editable=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Save
        super(Company, self).save(*args, **kwargs)

    def generate_automatic_slug(self, save=True):
        self.slug = slugify(self.title)
        if save:
            self.save()

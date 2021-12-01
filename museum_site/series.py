from django.db import models
from django.template.defaultfilters import slugify


class Series(models.Model):
    title = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, editable=False)
    description = models.TextField(default="")
    visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return "[" + str(self.id) + "] " + self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Series, self).save(*args, **kwargs)

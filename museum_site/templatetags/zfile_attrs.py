from django.template import Library
from museum_site.models import Review

register = Library()


@register.inclusion_tag("museum_site/subtemplate/tag/dummy-template.html")
def zfile_attrs(zfile, **kwargs):
    default_fields = ["id", "title", "letter"]
    fields = kwargs.get("fields", default_fields)
    output_format = kwargs.get("format", "table")
    template_name = "museum_site/subtemplate/tag/zfile-attrs-{}.html".format(output_format)
    attrs = zfile.get_all_attributes(include_staff_fields=True)
    feedback = Review.objects.filter(zfile_id=zfile.pk).order_by("title")
    return {"template": template_name, "zfile": zfile, "feedback": feedback}

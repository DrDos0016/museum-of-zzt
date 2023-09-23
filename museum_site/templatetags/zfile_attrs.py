from django.template import Library

register = Library()


@register.inclusion_tag("museum_site/subtemplate/tag/dummy-template.html")
def zfile_attrs(zfile, **kwargs):
    default_fields = ["id", "title", "letter"]
    fields = kwargs.get("fields", default_fields)
    output_format = kwargs.get("format", "table")
    template_name = "museum_site/subtemplate/tag/zfile-attrs-{}.html".format(output_format)
    attrs = zfile.get_all_attributes(include_staff_fields=True)

    output = {}
    if output_format == "table":
        for key, val in attrs.items():
            if isinstance(val, dict):
                for k, v in val.items():
                    output[k] = {"heading": (key + " - " + k).replace("_", " ").title(), "value": v}
                    used_key = k
            else:
                output[key] = {"heading": key.replace("_", " ").title(), "value": val}
                used_key = key

            if used_key in ["description"] and output[used_key]["value"] == "":
                output[used_key]["value"] = "<i>None</i>"

    return {"template": template_name, "attrs": output}

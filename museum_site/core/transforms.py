from django.template.defaultfilters import escape

from museum_site.constants import FORM_ANY, FORM_NONE


def range_select_choices(first, last, order="asc", allow_any=False, allow_unknown=False):
    years = range(first, last + 1)

    if order == "desc":
        years = years[::-1]

    output = list(zip(years, years))

    if allow_any:
        output.insert(0, ("any", FORM_ANY))

    if allow_unknown:
        output.append(("unk", "Unknown"))

    return output


def language_select_choices(languages, allow_any=False, allow_non_english=False):
    output = list(languages.items())

    if allow_non_english:
        output.append(("non-english", "Non-English"))

    if allow_any:
        output.insert(0, ("any", FORM_ANY))

    return output


def qs_manual_order(qs, ordering, field="pk", kind="int"):
    """ Return a queryset arranged by a given ordering """
    qs = list(qs)
    ordered = []
    temp_dict = {}

    for row in qs:
        temp_dict[getattr(row, field)] = row
    for i in ordering:
        if kind == "int":
            key = int(i)
        else:
            key = i
        ordered.append(temp_dict[key])
    return ordered


def qs_to_links(qs):
    output = ""
    html = "<a href='{}'>{}</a>, "
    for i in qs:
        output += html.format(i.get_absolute_url(), escape(i.title))
    return output[:-2]

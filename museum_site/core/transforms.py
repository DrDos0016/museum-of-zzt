def qs_to_select_choices(qs, text="{0}", val="{0.pk}", allow_any=False):
    """ Transform a queryset into a list suitable for Django's forms. """
    output = []

    if allow_any:
        output.append(("any", "- ANY -"))

    for i in qs:
        output.append(
            (str(val.format(i)), text.format(i))
        )
    return output

def qs_to_categorized_select_choices(qs, text="{0}", val="{0.pk}", category_order=None):
    output = []

    categories = {}
    for i in qs:
        if not categories.get(i.category):
            categories[i.category] = []
        categories[i.category].append(
            (str(i.pk), i.title)
        )

    if category_order is None:
        category_order = list(categories.keys())

    for key in category_order:
        output.append((key, categories[key]))

    return output

def range_select_choices(first, last, order="asc", allow_any=False, allow_unknown=False):
    years = range(first, last + 1)

    if order == "desc":
        years = years[::-1]

    output = list(zip(years, years))

    if allow_any:
        output.insert(0, ("any", "- ANY -"))

    if allow_unknown:
        output.append(("unk", "Unknown"))

    return output

def language_select_choices(languages, allow_any=False, allow_non_english=False):
    output = list(languages.items())

    if allow_non_english:
        output.append(("non-english", "Non-English"))

    if allow_any:
        output.insert(0, ("any", "- ANY -"))

    return output

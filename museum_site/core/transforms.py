def qs_to_select_choices(qs, text="{0}", val="{0.pk}", allow_any=False):
    """ Transform a queryset into a list suitable for Django's forms. """
    output = []

    if allow_any:
        output.append(("any", "- ANY -"))

    for i in qs:
        output.append(
            (val.format(i), text.format(i))
        )
    return output

def qs_to_categorized_select_choices(qs, text="TEXT", val="VAL", category_order=None):
    output = []

    categories = {}
    for i in qs:
        if not categories.get(i.category):
            categories[i.category] = []
        categories[i.category].append(
            (i.pk, i.title)
        )

    if category_order is None:
        category_order = list(categories.keys())

    for key in category_order:
        output.append((key, categories[key]))

    return output

from museum_site.constants import FORM_ANY, FORM_NONE

def any_plus(choices):
    """ Appends Any as an option to the choices for a form"""
    choices = list(choices)
    choices.insert(0, ("any", FORM_ANY))
    return choices


def get_sort_option_form_choices(options):
    output = []
    for i in options:
        output.append((i["val"], i["text"]))
    return output


def clean_params(p, list_items=[]):
    """ Returns a dictionary (request.GET/POST) with blank/"Any" values removed. List items are ignored """
    # TODO 2020-09-20 THIS SEEMS A BIT HARDCODED WITH THE LIST BELOW?
    to_delete = []
    for (k, v) in p.items():
        if k in list_items:
            continue
        if k in ["genre", "year", "lang", "reviews", "articles"]:
            if v.lower() == "any":
                to_delete.append(k)
        elif v.strip() == "":
            to_delete.append(k)
        else:
            p[k] = v.strip()
    for k in to_delete:
        del p[k]
    return p


def load_form(f, request, initial=None):
    if request.method == "POST":
        form = f(request.POST, request.FILES)
    elif initial:
        form = f(initial)
    else:
        form = f()
    return form

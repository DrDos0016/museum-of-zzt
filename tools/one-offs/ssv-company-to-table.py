import os
import sys

import django

from django.template.defaultfilters import slugify

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    print(
        "This script will analyze all File objects ssv_company value. "
        "It will then create Company model objects for all found company names"
    )
    input("Press Enter to begin")

    qs = File.objects.all().order_by("id")

    all_company_names = []
    for zf in qs:
        companies = zf.ssv_company.split("/")

        for company in companies:
            if company:
                all_company_names.append(company)

    all_company_names.sort()
    company_names = []
    last = "X!Y!Z!Z!Y"
    for c in all_company_names:
        if c == last:
            continue
        company_names.append(c)
        last = c

    created_count = 0
    for c in company_names:
        # Try and come up with a sensible slug
        (c_obj, created) = Company.objects.get_or_create(title=c, slug=slugify(c))
        created_count += 1 if created else 0

        # Some unique company names
        if c_obj.title == "⌂⌂⌂⌂ ⌂⌂⌂⌂⌂⌂⌂⌂⌂":
            c_obj.slug = "energizer"
        elif c_obj.title == "ファンタシ Software":
            c_obj.slug = "fantasy-software"
        elif c_obj.title == "妹Soft":
            c_obj.slug = "妹soft"

        c_obj.save()

    print("Created {} company objects.".format(created_count))
    print("Associating companies with zfiles...")
    qs = File.objects.all().order_by("id")

    association_count = 0
    for zf in qs:
        companies = zf.ssv_company.split("/")
        for company in companies:
            if company:
                zf.companies.add(Company.objects.filter(title=company).order_by("id").first())
                association_count += 1

    print("Added {} associations.".format(association_count))
    print("DONE.")
    return True


if __name__ == '__main__':
    main()

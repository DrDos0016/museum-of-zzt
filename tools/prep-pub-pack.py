import datetime
import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import *  # noqa: E402
from museum_site.constants import SITE_ROOT

now = datetime.datetime.now()
HEADER = """{% with "articles/2021/publish-<date>/" as path %}
<p></p>

""".replace("<date>", now.strftime("%b-%d").lower())

QUERY = """{% with "<ids_string>"|get_files_by_id as files %}

"""

ENTRY = """{% with files.<f_id> as file %}
<h2>"{{file.title}}" {% if file.author != "Unknown" %} by {{file.author}}{% endif %}{% if file.release_date %} ({{file.release_date.year}}){% endif %}</h2>
{% include "museum_site/blocks/file_detailed_block.html" %}
<p></p>
<div class="image-set">
    <img src='{% static path|add:"<thumb>-1.png" %}' class="screenshot-thumb">
    <img src='{% static path|add:"<thumb>-2.png" %}' class="screenshot-thumb">
    <img src='{% static path|add:"<thumb>-3.png" %}' class="screenshot-thumb">
</div>
{% endwith %}

"""

FOOTER = """{% endwith %}
{% patreon_plug %}
{% endwith %}
"""

def main():
    count = 0
    ids_string = ""
    ids = []
    thumbs = []

    while True:
        print("Count", count)
        f_id = input("File ID (blank to stop): ")

        if not f_id:
            break

        try:
            f_id_int = int(f_id)
        except ValueError:
            print("Invalid ID!")
            continue

        f = File.objects.filter(pk=f_id_int)
        if f:
            print(f[0])
        else:
            print("No File object found.")

        while True:
            prefix = input("Image Prefix: ")
            if prefix not in thumbs:
                break
            print("Prefix already used!")

        ids_string += f_id + ","
        ids.append(f_id)
        thumbs.append(prefix)
        count += 1

    print("Assembling...")
    output = HEADER
    output += QUERY.replace("<ids_string>", ids_string[:-1])

    for idx in range(0, len(ids)):
        entry = ENTRY.replace("<f_id>", ids[idx])
        entry = entry.replace("<thumb>", thumbs[idx])
        output += entry

    output += FOOTER

    with open(os.path.join(SITE_ROOT, "wip", "ppX.html"), "w") as fh:
        fh.write(output)
    print("Wrote wip/ppX.html")



    return True


if __name__ == '__main__':
    main()

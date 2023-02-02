import json
import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402

from upload_dump import data


def main():
    print("This script will use upload_dump.json to re-associate zfiles with their upload objects")
    print("THIS WILL IMPACT THE DATABASE")
    print("The path to the file is hardcoded to /var/projects/museum-of-zzt/tools/one-offs/upload_dump.json")
    input("Press ENTER to begin.")

    #data = json.loads("/var/projects/museum-of-zzt/tools/one-offs/upload_dump.json")
    for i in data:
        upload_pk = i["pk"]
        zfile_pk = i["fields"]["file"]
        #print(i)
        #print(upload_pk, zfile_pk)
        if zfile_pk:
            zf = File.objects.get(pk=zfile_pk)
            zf.upload_id = upload_pk
            zf.save()
            print("Associated ZFile #{} with Upload #{}".format(zfile_pk, upload_pk))


    return True


if __name__ == '__main__':
    main()

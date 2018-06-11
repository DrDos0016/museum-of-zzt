import glob
import os
import shutil
import sys
from zipfile import ZipFile

import django
from internetarchive import upload

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import File

ZGAMES_PATH = "/var/projects/museum"
BASE_PATH = "/var/projects/museum/museum_site/static/data/base/"

BASES = {
    "A": {
        "name": "ZZT v3.2 Registered",
        "directory": "ZZT32-REG",
        "use_cfg": True,
        "registered": True,
        "prefix": "zzt_",
        "executable": "ZZT.EXE",
    },
    "B": {
        "name": "ZZT v2.0 Shareware",
        "directory": "ZZT20-SW",
        "use_cfg": True,
        "registered": False,
        "prefix": "zzt_",
        "executable": "ZZT.EXE",
    }
}


def main():
    print("Internet Archive Publisher")
    while True:
        file_id = input("File ID: ")
        if not file_id:
            break

        # Load file
        f = File.objects.get(pk=int(file_id))
        print("Selected:", f, "(" + f.filename + ")")

        for base in BASES.keys():
            print("[" + base + "]", BASES[base]["name"])
        selected_base = input("Select package base: ").upper()
        base = BASES[selected_base]

        # Copy the zip
        zip_name = "zzt_" + f.filename
        shutil.copy(
            ZGAMES_PATH + f.download_url(),
            zip_name
        )

        # Open the WIP zip
        with ZipFile(zip_name, "a") as z:
            # Insert the base files
            to_add = glob.glob(
                os.path.join(BASE_PATH, base["directory"], "*")
            )
            for a in to_add:
                z.write(a, arcname=os.path.basename(a))

            # Create ZZT.CFG if needed
            if base["use_cfg"]:
                # Find the relevant files to default to
                file_list = z.namelist()
                for idx, name in enumerate(file_list, start=1):
                    print(idx, name)
                selected_idx = int(input("Launch which file? ")) - 1
                launch_file = z.namelist()[selected_idx]
                config_content = launch_file[:-4]  # Remove .ZZT extension
                if base["registered"]:
                    config_content += "\r\nREGISTERED"
                z.writestr("ZZT.CFG", config_content)

        # Zip file is completed, prepare the upload
        meta = {
            "title": f.title,
            "mediatype": "software",
            "collection": "open_source_software",
            "emulator": "dosbox",
            "emulator_ext": "zip",
            "emulator_start": base["executable"] + " " + launch_file,
            "year": str(f.release_date)[:4],
            "subject": ["zzt"] + f.genre.split("/"),
            "creator": f.author.split("/"),
            "description": "Game created using the ZZT engine."
        }

        print("Uploading to Internet Archive...")
        r = upload(
            base["prefix"] + f.filename[:-4],
            files=[zip_name],
            metadata=meta
        )

        if r[0].status_code == 200:
            print("Upload successful!")
            f.archive_name = base["prefix"] + f.filename[:-4]
            f.save()
            print("https://archive.org/details/" + f.archive_name)
            os.remove(zip_name)
        else:
            print("Upload failed!")
            print(r)
    return True


if __name__ == "__main__":
    main()

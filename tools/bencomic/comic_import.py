import glob
import json
import os
import sys

import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from bencomic.models import Comic


def main():
    files = glob.glob(
        "/var/projects/museum/tools/bencomic/necocone.co/text/*.txt"
    )
    files.sort()

    for file in files:
        json_file = os.path.basename(file).split(".")[0]+".json"

        """
        title = models.CharField(max_length=100)
        stripcreator_id = models.IntegerField()
        stripcreator_account = models.CharField(
            max_length=8, choices=STRIPCREATOR_ACCOUNTS
        )
        date = models.DateField(null=True, blank=True, default=None)
        transcript = models.TextField()
        """

        # THE PROVIDED TRANSCRIPTS ARE MISSING THE FINAL COMIC FYI
        if json_file in ["300194.json", "315742.json", "339786.json", "343172.json", "343685.json", "343692.json", "344154.json", "379835.json", "422436.json", "433523.json"]:
            comic = Comic(title="!!FIX ME!!",
                          stripcreator_id=int(json_file.replace(".json", "")),
                          stripcreator_account="bencomic",
                          transcript="")

            print(comic)
            comic.save()
            continue

        with open("/var/projects/museum/tools/bencomic/json/" + json_file) as fh:
            comic = Comic()
            data = fh.read()
            data = json.loads(data)

            comic = Comic(title=data["title"],
                          stripcreator_id=data["sc_id"],
                          stripcreator_account=data["author"],
                          date=data["date"])

            # Transcript
            transcript = ""
            panel_idx = 1
            for panel in data["panels"]:
                transcript += "-- Panel{} --\n".format(panel_idx)
                if panel.get("narration"):
                    transcript += "<Narration> " + panel["narration"] + "\n"
                if panel.get("dialog"):
                    if panel["dialog"].get("left") and panel["dialog"]["left"].get("text"):
                        transcript += "<Left> " + panel["dialog"]["left"]["text"] + "\n"
                    if panel["dialog"].get("right") and panel["dialog"]["right"].get("text"):
                        transcript += "<Right> " + panel["dialog"]["right"]["text"] + "\n"
                panel_idx += 1
            comic.transcript = transcript
            comic.save()
            print(comic)
    return True

if __name__ == "__main__":
    main()

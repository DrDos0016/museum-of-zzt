import os
import sys
import tempfile

from datetime import datetime, timedelta

from museum_site.constants import SITE_ROOT

PREFIX = "moz-"
PYTHON = os.path.join(SITE_ROOT, "venv", "bin", "python3")
BACKUPS = os.environ.get("MOZ_BACKUP_DIR", os.path.join(SITE_ROOT, "backups"))
TEMP_DIR = tempfile.TemporaryDirectory(prefix=PREFIX)
TEMP = TEMP_DIR.name
DUMP_SCRIPT = os.path.join(SITE_ROOT, "tools", "dump_database.py")
DB_BACKUP = os.path.join(TEMP, "database.sql")
TODAY = str(datetime.now())[:10]

def export_database():
    command = "{} {} {}".format(PYTHON, DUMP_SCRIPT, DB_BACKUP)
    os.system(command)
    return True


def compress_database():
    tar_name = os.path.join(BACKUPS, TODAY + "_database.tar.gz")
    command = "tar -czf {} -C {} {}".format(tar_name, TEMP, "database.sql")
    os.system(command)
    os.remove(os.path.join(TEMP, "database.sql"))
    return True


def compress_zgames():
    tar_name = os.path.join(BACKUPS, TODAY + "_zgames.tar.gz")
    command = "tar --exclude='mass/*' -czf {} -C {} zgames".format(tar_name, SITE_ROOT)
    os.system(command)
    return True

def compress_museum_sans_articles():
    tar_name = os.path.join(BACKUPS, TODAY + "_museum.tar.gz")
    command = "tar --exclude='.git' --exclude='venv' --exclude='zgames' --exclude='museum_site/static/articles' -czf {} -C {} museum-of-zzt".format(tar_name, os.path.join(SITE_ROOT, ".."))
    os.system(command)
    return True

def compress_previous_years_articles():
    comp = datetime.now()
    if comp.weekday() != 3:
        print("This backup is only updated weekly.", comp.weekday())
        return False
    tar_name = os.path.join(BACKUPS, "older_articles.tar.gz")
    command = "tar --exclude='{}' -czf {} -C {} articles".format(comp.year, tar_name, os.path.join(SITE_ROOT, "museum_site", "static"))
    os.system(command)


def compress_current_years_articles():
    YEAR = TODAY[:4]
    tar_name = os.path.join(BACKUPS, "{}_articles.tar.gz".format(YEAR))
    command = "tar -czf {} -C {} {}".format(tar_name, os.path.join(SITE_ROOT, "museum_site", "static", "articles"), YEAR)
    os.system(command)


def main():
    BACKUP_FUNCTIONS = [
        {"step": "Exporting database", "func": export_database},
        {"step": "Compressing database file", "func": compress_database},
        {"step": "Compressing /zgames/", "func": compress_zgames},
        {"step": "Compressing Museum (excluding static/articles/)", "func": compress_museum_sans_articles},
        {"step": "Compressing Previous Years' Articles", "func": compress_previous_years_articles},
        {"step": "Compressing This Year's Articles", "func": compress_current_years_articles},
    ]
    total_functions = len(BACKUP_FUNCTIONS)

    if not os.path.isdir(BACKUPS):
        print("Creating backups directory")
        os.makedirs(BACKUPS)

    idx = 1
    for i in BACKUP_FUNCTIONS:
        print("{} [{}/{}] {}".format(datetime.now(), idx, total_functions, i["step"]))
        i["func"]()
        idx += 1
    print("{} [FINISH] All backup functions completed.".format(datetime.now()))
    return True


if __name__ == "__main__":
    main()

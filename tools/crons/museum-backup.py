import os
import sys

from datetime import datetime

from museum_site.constants import SITE_ROOT


def main():
    PYTHON = os.path.join(SITE_ROOT, "venv", "bin", "python3")
    BACKUPS = os.path.join(SITE_ROOT, "backups")
    TEMP = os.path.join(SITE_ROOT, "temp")
    PROJECTS = "/var/projects"

    DUMP_SCRIPT = os.path.join(SITE_ROOT, "tools", "dump_database.py")
    DB_BACKUP = os.path.join(TEMP, "database.sql")

    today = str(datetime.now())[:10]

    print("[1/3] Backing up database", datetime.now())
    command = "{} {} {}".format(
        PYTHON,
        DUMP_SCRIPT,
        DB_BACKUP
    )
    #print(command)
    os.system(command)

    print("Compressing...")
    tar_name = os.path.join(BACKUPS, today + "_database.tar.gz")
    command = "tar -czf {} -C {} {}".format(
        tar_name,
        TEMP,
        "database.sql"
        )
    #print(command)
    os.system(command)
    os.remove(os.path.join(TEMP, "database.sql"))

    print("[2/3] Backing up /zgames", datetime.now())
    print("Compressing...")
    tar_name = os.path.join(BACKUPS, today + "_zgames.tar.gz")
    command = "tar --exclude='mass/*' -czf {} -C {} zgames".format(
        tar_name,
        SITE_ROOT,
    )
    #print(command)
    os.system(command)


    print("[3/3] Backing up museum", datetime.now())
    print("Compressing...")
    tar_name = os.path.join(BACKUPS, today + "_museum.tar.gz")
    command = "tar --exclude='.git' --exclude='backups/*' --exclude='log/*' --exclude='temp/*' --exclude='venv' --exclude='zgames' -czf {} -C {} museum-of-zzt".format(
        tar_name,
        PROJECTS,
    )
    print(command)
    os.system(command)
    print("DONE.", datetime.now())

    return True

if __name__ == "__main__":
    main()

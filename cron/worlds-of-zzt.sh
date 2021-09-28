#!/bin/bash
source /var/projects/museum-of-zzt/.env
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE;
export PYTHONPATH=$PYTHONPATH;
echo "CRON START: Worlds of ZZT Bot";
date;
echo "------------------------------------------------------------";
/var/projects/museum-of-zzt/venv/bin/python \
/var/projects/museum-of-zzt/tools/crons/worlds-of-zzt.py 2>&1
echo "CRON END: Worlds of ZZT Bot";
date;
echo "============================================================";

#!/bin/bash
set -a
source $HOME/env/$HOSTNAME-museum-of-zzt.env;
set +a
echo "CRON START: ";
date;
echo "------------------------------------------------------------";
$HOME/projects/museum-of-zzt/venv/bin/python3 $HOME/projects/museum-of-zzt/manage.py delete-abandoned-signups
echo "CRON END: ";
date;
echo "============================================================";

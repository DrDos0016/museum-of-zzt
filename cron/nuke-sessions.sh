#!/bin/bash
set -a
source $HOME/env/$HOSTNAME-museum-of-zzt.env;
set +a
echo "CRON START: Nuke Empty Sessions";
date;
echo "------------------------------------------------------------";
$HOME/projects/museum-of-zzt/venv/bin/python3 $HOME/projects/museum-of-zzt/manage.py nuke-sessions 2>&1
echo "CRON END: Nuked Empty Sessions";
date;
echo "============================================================";

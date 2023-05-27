#!/bin/bash
set -a
source $HOME/env/$HOSTNAME-museum-of-zzt.env;
set +a
echo "CRON START: Museum Backup";
date;
echo "------------------------------------------------------------";
$HOME/projects/museum-of-zzt/venv/bin/python3 $HOME/projects/museum-of-zzt/tools/crons/museum-backup.py 2>&1
echo "CRON END: Museum Backup";
date;
echo "============================================================";

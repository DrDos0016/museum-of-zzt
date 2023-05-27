#!/bin/bash
set -a
source $HOME/env/$HOSTNAME-museum-of-zzt.env;
set +a
echo "CRON START: Patreon Scan";
date;
echo "------------------------------------------------------------";
$HOME/projects/museum-of-zzt/venv/bin/python3 $HOME/projects/museum-of-zzt/tools/crons/patreon-scan.py 2>&1
echo "CRON END: Patreon Scan";
date;
echo "============================================================";

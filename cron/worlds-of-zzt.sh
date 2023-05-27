#!/bin/bash
set -a
source $HOME/env/$HOSTNAME-museum-of-zzt.env;
set +a
echo "CRON START: Worlds of ZZT Bot";
date;
echo "------------------------------------------------------------";
$HOME/projects/museum-of-zzt/venv/bin/python $HOME/projects/museum-of-zzt/tools/crons/worlds-of-zzt.py 2>&1
echo "CRON END: Worlds of ZZT Bot";
date;
echo "============================================================";

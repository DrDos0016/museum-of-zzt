#!/bin/bash
set -a
source $HOME/env/$HOSTNAME-museum-of-zzt.env;
set +a
pkill -f "python3 $HOME/projects/museum-of-zzt/discord/bot.py"
$HOME/projects/museum-of-zzt/venv/bin/python3 $HOME/projects/museum-of-zzt/discord/bot.py >> $HOME/projects/museum-of-zzt/log/discord.log 2>&1 &

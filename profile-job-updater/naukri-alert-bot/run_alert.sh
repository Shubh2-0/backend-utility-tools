#!/bin/bash
# Cron wrapper for Java job alert bot
# Logs go to ~/naukri-alert-bot/cron.log

set -u
cd "$HOME/naukri-alert-bot"

PYTHON_BIN="$HOME/NopeRi/.venv/bin/python"
[ -x "$PYTHON_BIN" ] || PYTHON_BIN="$HOME/NopeRi/venv/bin/python"
[ -x "$PYTHON_BIN" ] || PYTHON_BIN="/usr/bin/python3"

LOCK="$HOME/naukri-alert-bot/.lock"
exec 9>"$LOCK"
flock -n 9 || { echo "$(date) - already running, skip" >> "$HOME/naukri-alert-bot/cron.log"; exit 0; }

"$PYTHON_BIN" "$HOME/naukri-alert-bot/alert_bot.py" >> "$HOME/naukri-alert-bot/cron.log" 2>&1

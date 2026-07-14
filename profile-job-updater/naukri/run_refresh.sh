#!/bin/bash
# Wrapper for cron to run NopeRi daily refresh
cd /home/ubuntu/NopeRi
/home/ubuntu/NopeRi/.venv/bin/python daily_refresh.py >> /home/ubuntu/NopeRi/cron.log 2>&1

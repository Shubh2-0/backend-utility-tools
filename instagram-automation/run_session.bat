@echo off
cd /d "%~dp0"
python auto_commenter.py --max-comments 10 >> session_log.txt 2>&1

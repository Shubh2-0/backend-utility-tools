@echo off
echo ============================================
echo  Maa Kaali Creations - Auto Commenter Setup
echo  Setting up 3 daily sessions via Task Scheduler
echo ============================================
echo.

set SCRIPT_PATH=%~dp0run_session.bat

echo Creating Morning session (9:00 AM)...
schtasks /create /tn "MaaKaaliCreations_Morning" /tr "%SCRIPT_PATH%" /sc daily /st 09:00 /f
echo.

echo Creating Afternoon session (2:00 PM)...
schtasks /create /tn "MaaKaaliCreations_Afternoon" /tr "%SCRIPT_PATH%" /sc daily /st 14:00 /f
echo.

echo Creating Evening session (8:00 PM)...
schtasks /create /tn "MaaKaaliCreations_Evening" /tr "%SCRIPT_PATH%" /sc daily /st 20:00 /f
echo.

echo ============================================
echo  DONE! 3 sessions scheduled:
echo    Morning   - 9:00 AM  (10 comments)
echo    Afternoon - 2:00 PM  (10 comments)
echo    Evening   - 8:00 PM  (10 comments)
echo ============================================
echo.
echo To remove: run remove_scheduler.bat
pause

@echo off
echo Removing scheduled tasks...
schtasks /delete /tn "MaaKaaliCreations_Morning" /f
schtasks /delete /tn "MaaKaaliCreations_Afternoon" /f
schtasks /delete /tn "MaaKaaliCreations_Evening" /f
echo Done! All scheduled tasks removed.
pause

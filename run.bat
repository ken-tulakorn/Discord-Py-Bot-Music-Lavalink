@echo off
title Bot Music
color 3
cls

:loop
echo Starting the bot...
python index.py
echo Bot crashed or stopped. Restarting...
pause
goto loop

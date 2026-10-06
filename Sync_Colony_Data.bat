@echo off
REM ======================================================
REM FishNET 1-Click Master Colony & Breeding Sync Launcher
REM ======================================================
echo Running FishNET Synchronization Pipeline...
python scripts\sync_all_pipeline.py
echo.
echo Complete! Press any key to exit.
pause

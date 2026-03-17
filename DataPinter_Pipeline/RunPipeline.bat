@echo off
REM ================================
REM Pipeline ETL from DataPinter
REM ================================

REM Set Python Path
SET PYTHON_PATH=C:\Users\user2\AppData\Local\Programs\Python\Python313\python.exe
REM Set Working Dir
cd /d [PUT WORKING DIR HERE]


REM Run pipeline.py scripts
"%PYTHON_PATH%" pipeline.py

REM Pause
pause

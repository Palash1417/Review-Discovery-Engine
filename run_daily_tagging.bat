@echo off
REM Runs one daily chunk of AI tagging for the 2,033-review dataset.
REM Invoked by the Windows scheduled task "SpotifyDiscoveryTagging".
cd /d "C:\Users\palas\OneDrive\Documents\NextLeap\Graduation Project\Graduation project2"
echo ================================================== >> tag2000_daily.log
echo Run started: %DATE% %TIME% >> tag2000_daily.log
"C:\Users\palas\AppData\Local\Programs\Python\Python312\python.exe" tag_2000_daily.py >> tag2000_daily.log 2>&1
echo Run finished: %DATE% %TIME% >> tag2000_daily.log

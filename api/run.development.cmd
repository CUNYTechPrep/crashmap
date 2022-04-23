@echo off
setlocal
call:loadEnvs ..\.env ..\.env.development ..\.env.local ..\.env.development.local
flask run
exit /B %errorlevel%
endlocal

:loadEnvs
:loadEnv
if "%1" == "" exit /B 0
if exist %1 (
    for /f "eol=# tokens=*" %%i in (%1) do set %%i
    echo Loaded environment variables from %1.
) else (
    echo %1 not found.
)
shift
goto loadEnv

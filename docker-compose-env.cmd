@echo off
setlocal
call:loadEnvs .env .env.%1 .env.local .env.%1.local
docker-compose -f "docker-compose.%1.yml" "%2"
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

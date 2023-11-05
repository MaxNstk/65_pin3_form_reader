@echo off
setlocal enabledelayedexpansion

set "base_path=%~dp0"

:: Add the relative directory to the PATH
set "relative_path=poppler-23.08.0\Library\bin"
set "full_path=%base_path%%relative_path%;%PATH%"

:: Update the PATH environment variable
setx PATH "!full_path!" /M

:: Display a message
echo Directory added to PATH: %full_path%

:: End of script
endlocal
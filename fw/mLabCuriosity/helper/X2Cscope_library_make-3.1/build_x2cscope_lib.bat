@echo off
setlocal enabledelayedexpansion
rem ---------------------------------------------------------------------------
rem Builds the X2Cscope library for dsPIC33A (generic-32dsp-ak) with XC-DSC,
rem copies it into ..\..\X2Cscope and test-builds the mLabCuriosity firmware.
rem Log: build_x2cscope_lib.log (next to this script)
rem ---------------------------------------------------------------------------
cd /d "%~dp0"
set LOG=%~dp0build_x2cscope_lib.log
set XCDSC=C:\Program Files\Microchip\xc-dsc\v4.00\bin
if not exist "%XCDSC%\xc-dsc-gcc.exe" (
  for /d %%D in ("C:\Program Files\Microchip\xc-dsc\v*") do if exist "%%D\bin\xc-dsc-gcc.exe" set XCDSC=%%D\bin
)
set CC="%XCDSC%\xc-dsc-gcc.exe"
set AR="%XCDSC%\xc-dsc-ar.exe"
set LIB=libx2cscope-generic-32dsp-dspic33a-elf.a
set OBJ=_OBJ32DSPAK
set RC=0

echo X2Cscope library build %DATE% %TIME% > "%LOG%"
echo Compiler: %CC% >> "%LOG%"
%CC% --version >> "%LOG%" 2>&1 || (echo ERROR: xc-dsc-gcc not found >> "%LOG%" & set RC=1 & goto :end)

if exist %OBJ% rmdir /s /q %OBJ%
mkdir %OBJ%
if not exist dist mkdir dist
if exist dist\%LIB% del /q dist\%LIB%

echo. >> "%LOG%"
echo === Compiling library sources (-mcpu=generic-32dsp-ak -O2) === >> "%LOG%"
for %%F in (X2CScope\src\*.c) do (
  echo %%~nxF >> "%LOG%"
  %CC% -mcpu=generic-32dsp-ak -DX2C_GENERIC_MICROCHIP_DSPIC33A -IX2CScope\inc -Iinterface -O2 -c "%%F" -o %OBJ%\generic-32dsp-ak%%~nF.o >> "%LOG%" 2>&1
  if errorlevel 1 set RC=1
)
if !RC! neq 0 (echo ERROR: library compile failed >> "%LOG%" & goto :end)

rem xc-dsc-ar does not expand wildcards on Windows -> pass the object list explicitly
set LIBOBJS=
for %%O in (%OBJ%\*.o) do set LIBOBJS=!LIBOBJS! %%O
echo === Archiving:!LIBOBJS! === >> "%LOG%"
%AR% -omf=elf -r dist\%LIB% !LIBOBJS! >> "%LOG%" 2>&1
if errorlevel 1 (echo ERROR: archive failed >> "%LOG%" & set RC=1 & goto :end)
copy /y dist\%LIB% ..\..\X2Cscope\%LIB% >> "%LOG%"
echo Library OK: dist\%LIB% copied to X2Cscope\ >> "%LOG%"

rem ---------------- test build of the firmware -------------------------------
echo. >> "%LOG%"
echo === Test build of mLabCuriosity firmware === >> "%LOG%"
set PRJ=%~dp0..\..
set DFP=%USERPROFILE%\.mchp_packs\Microchip\dsPIC33AK-MP_DFP\1.6.273\xc16
set TB=%PRJ%\_build\x2c_testbuild
if exist "%TB%" rmdir /s /q "%TB%"
mkdir "%TB%"
set CFLAGS=-g -mcpu=33AK512MPS506 -O0 -msmart-io=1 -Wall -msfr-warn=off -mdfp="%DFP%"
set OBJS=
for %%F in ("%PRJ%\config.mcc\main.c" "%PRJ%\X2Cscope\X2Cscope.c" "%PRJ%\X2Cscope\X2CscopeComm.c") do (
  echo %%~nxF >> "%LOG%"
  %CC% %CFLAGS% -c "%%~F" -o "%TB%\%%~nF.o" >> "%LOG%" 2>&1
  if errorlevel 1 set RC=1
  set OBJS=!OBJS! "%TB%\%%~nF.o"
)
for /r "%PRJ%\config.mcc\mcc_generated_files" %%F in (*.c) do (
  echo %%~nxF >> "%LOG%"
  %CC% %CFLAGS% -c "%%F" -o "%TB%\%%~nF.o" >> "%LOG%" 2>&1
  if errorlevel 1 set RC=1
  set OBJS=!OBJS! "%TB%\%%~nF.o"
)
for /r "%PRJ%\config.mcc\mcc_generated_files" %%F in (*.s) do (
  echo %%~nxF >> "%LOG%"
  %CC% -g -mcpu=33AK512MPS506 -Wa,--no-relax -mdfp="%DFP%" -c "%%F" -o "%TB%\%%~nF_s.o" >> "%LOG%" 2>&1
  if errorlevel 1 set RC=1
  set OBJS=!OBJS! "%TB%\%%~nF_s.o"
)
if !RC! neq 0 (echo ERROR: firmware compile failed >> "%LOG%" & goto :end)
%CC% -mcpu=33AK512MPS506 -mdfp="%DFP%" -o "%TB%\test.elf" !OBJS! "%PRJ%\X2Cscope\%LIB%" -Wl,--script=p33AK512MPS506.gld,--stack=16,--check-sections,--data-init,--pack-data,--handles,--isr,--no-gc-sections,--fill-upper=0,--stackguard=16,--no-force-link,--smart-io,--report-mem,-Map="%TB%\test.map" >> "%LOG%" 2>&1
if errorlevel 1 (echo ERROR: firmware link failed >> "%LOG%" & set RC=1 & goto :end)
echo Firmware test build OK: %TB%\test.elf >> "%LOG%"

:end
echo. >> "%LOG%"
echo RESULT=%RC% >> "%LOG%"
endlocal

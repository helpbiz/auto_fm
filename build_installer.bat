@echo off
REM Auto FM 인스톨러 빌드 스크립트
REM Inno Setup을 사용하여 Windows 인스톨러 생성

echo ====================================================================
echo Auto FM 인스톨러 빌드 시작
echo ====================================================================
echo.

REM 실행 파일 확인
if not exist "dist\AutoFM.exe" (
    echo [오류] dist\AutoFM.exe 파일이 없습니다!
    echo 먼저 build.bat 를 실행하여 실행 파일을 빌드하세요.
    pause
    exit /b 1
)

REM Inno Setup 설치 확인
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
    echo [오류] Inno Setup이 설치되지 않았습니다.
    echo.
    echo 다운로드: https://jrsoftware.org/isdl.php
    echo 설치 후 다시 실행하세요.
    pause
    exit /b 1
)

echo [1/2] 이전 인스톨러 정리 중...
if exist installer_output rmdir /s /q installer_output
mkdir installer_output
echo 정리 완료.
echo.

echo [2/2] Inno Setup으로 인스톨러 생성 중...
%ISCC% installer.iss

if errorlevel 1 (
    echo.
    echo [오류] 인스톨러 빌드 실패!
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo 인스톨러 빌드 성공!
echo ====================================================================
echo.
echo 인스톨러 위치: installer_output\AutoFM_Setup_v1.0.0.exe
echo.
dir "installer_output\*.exe"
echo.
echo 다음 단계:
echo 1. 인스톨러를 다른 PC에서 테스트
echo 2. 프로그램 설치 및 동작 확인
echo 3. 제어판에서 제거 프로그램 테스트
echo.

pause

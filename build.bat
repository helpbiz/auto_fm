@echo off
REM Auto FM 실행 파일 빌드 스크립트
REM PyInstaller를 사용하여 단일 .exe 파일 생성

echo ====================================================================
echo Auto FM 빌드 시작
echo ====================================================================
echo.

REM PyInstaller 설치 확인
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [오류] PyInstaller가 설치되지 않았습니다.
    echo pip install pyinstaller 를 실행하세요.
    pause
    exit /b 1
)

echo [1/3] 이전 빌드 정리 중...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo 정리 완료.
echo.

echo [2/3] PyInstaller로 실행 파일 빌드 중...
echo 이 작업은 몇 분 소요될 수 있습니다...
pyinstaller auto_fm.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo [오류] 빌드 실패!
    pause
    exit /b 1
)

echo.
echo [3/3] 빌드 완료 확인...
if exist "dist\AutoFM.exe" (
    echo.
    echo ====================================================================
    echo 빌드 성공!
    echo ====================================================================
    echo.
    echo 실행 파일 위치: dist\AutoFM.exe
    echo 파일 크기:
    dir "dist\AutoFM.exe" | find "AutoFM.exe"
    echo.
    echo 다음 단계:
    echo 1. dist\AutoFM.exe 를 직접 실행하여 테스트
    echo 2. build_installer.bat 를 실행하여 인스톨러 생성
    echo.
) else (
    echo [오류] 실행 파일이 생성되지 않았습니다!
    pause
    exit /b 1
)

pause

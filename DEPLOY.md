# 원가산정 집계 시스템 배포 가이드

> **버전**: 2.0
> **최종 수정일**: 2026-02-14
> **대상**: 개발자 및 배포 담당자

---

## 📑 목차

1. [개요](#1-개요)
2. [빌드 준비](#2-빌드-준비)
3. [PyInstaller를 사용한 exe 빌드](#3-pyinstaller를-사용한-exe-빌드)
4. [배포 패키지 생성](#4-배포-패키지-생성)
5. [버전 관리](#5-버전-관리)
6. [배포 체크리스트](#6-배포-체크리스트)
7. [문제 해결](#7-문제-해결)
8. [부록](#8-부록)

---

## 1. 개요

### 1.1 배포 개요

원가산정 집계 시스템은 Python 애플리케이션을 Windows 실행 파일(.exe)로 변환하여 배포합니다.

**배포 방식**:
- **방법 1**: 단일 exe 파일 (권장)
- **방법 2**: exe + 폴더 구조

**배포 도구**:
- **PyInstaller**: Python → exe 변환 도구

### 1.2 배포 플로우

```
[소스 코드] → [빌드 준비] → [PyInstaller 실행] → [exe 생성] → [테스트] → [배포 패키지 생성] → [배포]
```

### 1.3 빌드 환경 요구사항

| 구성 요소 | 버전 | 비고 |
|----------|------|------|
| Python | 3.12+ | 빌드 환경 |
| PyInstaller | 6.0+ | exe 빌드 도구 |
| Windows | 10/11 | 빌드 OS |
| 디스크 공간 | 2GB+ | 빌드 중 임시 파일 |

---

## 2. 빌드 준비

### 2.1 PyInstaller 설치

#### 2.1.1 기본 설치

```bash
pip install pyinstaller
```

#### 2.1.2 설치 확인

```bash
pyinstaller --version
```

**예상 출력**:
```
6.3.0
```

### 2.2 빌드 환경 정리

#### 2.2.1 이전 빌드 삭제

이전 빌드 파일이 있다면 삭제:

```bash
# Windows Command Prompt
rmdir /s /q build
rmdir /s /q dist

# PowerShell
Remove-Item -Recurse -Force build, dist

# Git Bash
rm -rf build dist
```

#### 2.2.2 __pycache__ 정리

```bash
# PowerShell
Get-ChildItem -Recurse -Filter __pycache__ | Remove-Item -Recurse -Force

# Git Bash
find . -type d -name __pycache__ -exec rm -rf {} +
```

### 2.3 버전 정보 파일 생성

#### 2.3.1 file_version_info.txt 생성

PyInstaller는 exe 파일의 버전 정보를 설정할 수 있습니다.

**file_version_info.txt**:
```python
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2, 0, 0, 0),
    prodvers=(2, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'원가산정 시스템 개발팀'),
          StringStruct(u'FileDescription', u'원가산정 집계 시스템'),
          StringStruct(u'FileVersion', u'2.0.0.0'),
          StringStruct(u'InternalName', u'auto_fm'),
          StringStruct(u'LegalCopyright', u'Copyright (C) 2024-2026'),
          StringStruct(u'OriginalFilename', u'auto_fm.exe'),
          StringStruct(u'ProductName', u'원가산정 집계 시스템'),
          StringStruct(u'ProductVersion', u'2.0.0.0')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
```

### 2.4 spec 파일 생성 (선택)

PyInstaller는 `.spec` 파일을 사용하여 빌드를 세밀하게 제어할 수 있습니다.

#### 2.4.1 기본 spec 파일 생성

```bash
pyi-makespec --onefile --windowed src/main.py
```

생성된 `main.spec` 파일을 `auto_fm.spec`으로 이름 변경:

```bash
move main.spec auto_fm.spec
```

#### 2.4.2 auto_fm.spec 커스터마이즈

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data', 'data'),  # 데이터 파일 포함
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='auto_fm',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 애플리케이션
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='file_version_info.txt',
    icon='icon.ico'  # 아이콘 파일 (있는 경우)
)
```

---

## 3. PyInstaller를 사용한 exe 빌드

### 3.1 기본 빌드

#### 3.1.1 단일 파일 빌드 (권장)

모든 파일을 하나의 exe로 패키징:

```bash
pyinstaller --onefile --windowed --name auto_fm src/main.py
```

**옵션 설명**:
- `--onefile`: 단일 exe 파일로 빌드
- `--windowed`: 콘솔 창 숨김 (GUI 앱)
- `--name auto_fm`: 출력 파일명

#### 3.1.2 폴더 기반 빌드

exe + 의존성 파일들을 폴더로 구성:

```bash
pyinstaller --windowed --name auto_fm src/main.py
```

### 3.2 고급 빌드 옵션

#### 3.2.1 아이콘 추가

```bash
pyinstaller --onefile --windowed --name auto_fm --icon=icon.ico src/main.py
```

`icon.ico` 파일을 프로젝트 루트에 배치해야 합니다.

#### 3.2.2 버전 정보 추가

```bash
pyinstaller --onefile --windowed --name auto_fm --version-file=file_version_info.txt src/main.py
```

#### 3.2.3 데이터 파일 포함

```bash
pyinstaller --onefile --windowed --name auto_fm --add-data "data;data" src/main.py
```

> **참고**: Windows에서는 세미콜론(;), Linux/Mac에서는 콜론(:) 사용

#### 3.2.4 모든 옵션 조합

```bash
pyinstaller --onefile --windowed --name auto_fm --icon=icon.ico --version-file=file_version_info.txt --add-data "data;data" src/main.py
```

### 3.3 spec 파일 사용 빌드

spec 파일을 사용하면 매번 긴 명령을 입력할 필요가 없습니다:

```bash
pyinstaller auto_fm.spec
```

### 3.4 빌드 스크립트 생성

#### 3.4.1 build.bat (Windows)

빌드 과정을 자동화하는 배치 파일:

```batch
@echo off
echo ================================================
echo      원가산정 시스템 빌드 스크립트
echo ================================================
echo.

REM 이전 빌드 삭제
echo [1/4] 이전 빌드 정리 중...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist auto_fm.spec del auto_fm.spec

REM 가상 환경 활성화
echo [2/4] 가상 환경 활성화 중...
call venv\Scripts\activate.bat

REM PyInstaller 설치 확인
echo [3/4] PyInstaller 확인 중...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller가 설치되어 있지 않습니다. 설치 중...
    pip install pyinstaller
)

REM 빌드 실행
echo [4/4] exe 빌드 중...
pyinstaller --onefile --windowed --name auto_fm --version-file=file_version_info.txt src/main.py

echo.
echo ================================================
echo      빌드 완료!
echo      출력 파일: dist\auto_fm.exe
echo ================================================
pause
```

**사용 방법**:
```bash
build.bat
```

#### 3.4.2 build.sh (Linux/Mac)

```bash
#!/bin/bash

echo "================================================"
echo "      원가산정 시스템 빌드 스크립트"
echo "================================================"
echo ""

# 이전 빌드 삭제
echo "[1/4] 이전 빌드 정리 중..."
rm -rf build dist auto_fm.spec

# 가상 환경 활성화
echo "[2/4] 가상 환경 활성화 중..."
source venv/bin/activate

# PyInstaller 설치 확인
echo "[3/4] PyInstaller 확인 중..."
if ! pip show pyinstaller > /dev/null 2>&1; then
    echo "PyInstaller가 설치되어 있지 않습니다. 설치 중..."
    pip install pyinstaller
fi

# 빌드 실행
echo "[4/4] exe 빌드 중..."
pyinstaller --onefile --windowed --name auto_fm --version-file=file_version_info.txt src/main.py

echo ""
echo "================================================"
echo "      빌드 완료!"
echo "      출력 파일: dist/auto_fm"
echo "================================================"
```

실행 권한 부여:
```bash
chmod +x build.sh
./build.sh
```

### 3.5 빌드 확인

빌드가 완료되면 다음 파일들이 생성됩니다:

```
dist/
└── auto_fm.exe     # 실행 파일

build/
└── auto_fm/        # 빌드 중간 파일 (삭제 가능)

auto_fm.spec        # spec 파일 (재사용 가능)
```

**파일 크기 확인**:
```bash
# Windows
dir dist\auto_fm.exe

# Linux/Mac
ls -lh dist/auto_fm
```

**예상 크기**: 50-100MB (PyQt6 포함)

---

## 4. 배포 패키지 생성

### 4.1 배포 파일 구성

사용자에게 배포할 최종 패키지는 다음과 같이 구성합니다:

```
auto_fm_v2.0/
├── auto_fm.exe         # 실행 파일
├── README.txt          # 간단한 사용 설명
├── USER_GUIDE.md       # 사용자 매뉴얼
└── data/               # 초기 데이터 (선택)
    └── example_scenario.json
```

### 4.2 README.txt 생성

**README.txt**:
```
============================================
   원가산정 집계 시스템 v2.0
============================================

□ 설치 방법
  1. auto_fm.exe 파일을 원하는 폴더에 복사합니다.
  2. auto_fm.exe를 더블클릭하여 실행합니다.

□ 첫 실행
  - 처음 실행 시 cost_calc.db 파일이 자동으로 생성됩니다.
  - Windows Defender 경고가 나타날 수 있습니다.
    → "추가 정보" → "실행" 버튼을 클릭하세요.

□ 상세 사용법
  - USER_GUIDE.md 파일을 참조하세요.

□ 지원
  - 이메일: support@example.com
  - 전화: 02-XXXX-XXXX

□ 버전 정보
  - 버전: 2.0
  - 날짜: 2026-02-14
  - Python: 3.12
  - PyQt6: 6.6

============================================
© 2024-2026 원가산정 시스템. All rights reserved.
============================================
```

### 4.3 ZIP 패키지 생성

#### 4.3.1 수동 압축

1. `dist` 폴더로 이동
2. 필요한 파일 복사:
   - auto_fm.exe
   - README.txt
   - USER_GUIDE.md
3. 폴더 선택 → 우클릭 → "압축"
4. `auto_fm_v2.0.zip` 생성

#### 4.3.2 자동 압축 스크립트

**package.bat**:
```batch
@echo off
set VERSION=2.0
set PKG_NAME=auto_fm_v%VERSION%

echo ================================================
echo      배포 패키지 생성 중...
echo ================================================

REM 패키지 폴더 생성
if exist %PKG_NAME% rmdir /s /q %PKG_NAME%
mkdir %PKG_NAME%

REM 파일 복사
copy dist\auto_fm.exe %PKG_NAME%\
copy README.txt %PKG_NAME%\
copy USER_GUIDE.md %PKG_NAME%\

REM ZIP 압축 (PowerShell 사용)
powershell Compress-Archive -Path %PKG_NAME% -DestinationPath %PKG_NAME%.zip -Force

echo.
echo 배포 패키지 생성 완료: %PKG_NAME%.zip
pause
```

### 4.4 설치 프로그램 생성 (선택)

#### 4.4.1 Inno Setup 사용

Inno Setup을 사용하면 전문적인 설치 프로그램을 만들 수 있습니다.

**1단계: Inno Setup 다운로드**

[Inno Setup](https://jrsoftware.org/isinfo.php) 다운로드 및 설치

**2단계: 스크립트 작성 (installer.iss)**

```ini
[Setup]
AppName=원가산정 집계 시스템
AppVersion=2.0
DefaultDirName={pf}\AutoFM
DefaultGroupName=원가산정 시스템
OutputDir=installer_output
OutputBaseFilename=auto_fm_setup_v2.0
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\auto_fm.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "USER_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\원가산정 시스템"; Filename: "{app}\auto_fm.exe"
Name: "{userdesktop}\원가산정 시스템"; Filename: "{app}\auto_fm.exe"

[Run]
Filename: "{app}\auto_fm.exe"; Description: "프로그램 실행"; Flags: postinstall nowait skipifsilent
```

**3단계: 설치 프로그램 빌드**

1. Inno Setup Compiler 실행
2. File → Open → installer.iss 선택
3. Build → Compile
4. `installer_output/auto_fm_setup_v2.0.exe` 생성

---

## 5. 버전 관리

### 5.1 시맨틱 버저닝

버전 번호는 `MAJOR.MINOR.PATCH` 형식을 따릅니다.

```
2.0.1
│ │ └── PATCH: 버그 수정, 작은 변경
│ └──── MINOR: 새로운 기능 추가 (하위 호환)
└────── MAJOR: 큰 변경, 하위 호환 불가
```

**예시**:
- `2.0.0`: 메이저 업데이트 (전면 개편)
- `2.1.0`: 마이너 업데이트 (시나리오 비교 기능 추가)
- `2.1.1`: 패치 (버그 수정)

### 5.2 버전 정보 업데이트

#### 5.2.1 src/version.py 생성

```python
# src/version.py

__version__ = "2.0.0"
__author__ = "원가산정 시스템 개발팀"
__email__ = "support@example.com"
__release_date__ = "2026-02-14"
```

#### 5.2.2 main.py에서 버전 정보 표시

```python
# src/main.py

from src.version import __version__

def main():
    print(f"원가산정 집계 시스템 v{__version__}")
    # ... 나머지 코드
```

#### 5.2.3 file_version_info.txt 업데이트

버전 업데이트 시 `file_version_info.txt`의 버전 정보도 함께 업데이트:

```python
filevers=(2, 1, 0, 0),  # 2.1.0
prodvers=(2, 1, 0, 0),
```

### 5.3 변경 이력 관리

#### 5.3.1 CHANGELOG.md 생성

```markdown
# 변경 이력

## [2.0.0] - 2026-02-14

### Added
- 시나리오 비교 기능 추가
- PDF/Excel 내보내기 기능
- 사용자 정의 직무 관리

### Changed
- UI 전면 개편
- 계산 로직 최적화

### Fixed
- 드롭다운 선택 오류 수정
- Dirty flag 초기화 문제 해결

## [1.0.0] - 2024-10-01

### Added
- 초기 릴리스
```

---

## 5. 롤백 절차 / Rollback Procedure

배포 후 문제가 발생했을 때 이전 버전으로 신속하게 복구하는 절차입니다.

### 5.1 롤백이 필요한 상황

다음과 같은 경우 롤백을 고려해야 합니다:

**긴급 롤백 (즉시)**:
- [ ] 프로그램이 실행되지 않음 (치명적 오류)
- [ ] 데이터 손실 또는 손상 발생
- [ ] 계산 결과가 심각하게 잘못됨
- [ ] 보안 취약점 발견

**일반 롤백 (검토 후)**:
- [ ] 새로운 기능이 정상 동작하지 않음
- [ ] 성능 저하 발생
- [ ] 사용자 불편 사항 다수 발생
- [ ] 특정 환경에서만 문제 발생

### 5.2 사전 준비 사항

롤백을 원활하게 진행하기 위해 배포 시 다음 사항을 준비해야 합니다:

#### 5.2.1 이전 버전 백업

**배포 전 체크리스트**:
- [ ] 이전 버전 exe 파일 별도 폴더에 보관
- [ ] 이전 버전 소스 코드 Git 태그 생성
- [ ] 이전 버전 데이터베이스 스키마 백업
- [ ] 이전 버전 문서 백업

**백업 디렉터리 구조**:
```
backups/
├── v1.0.0/
│   ├── auto_fm_v1.0.0.exe
│   ├── cost_calc_v1.0.0.db (스키마)
│   ├── USER_GUIDE_v1.0.0.md
│   └── release_notes_v1.0.0.txt
├── v1.1.0/
│   ├── auto_fm_v1.1.0.exe
│   └── ...
└── v2.0.0/
    ├── auto_fm_v2.0.0.exe
    └── ...
```

#### 5.2.2 Git 태그 관리

배포 시 Git 태그를 생성하여 특정 시점으로 쉽게 돌아갈 수 있도록 합니다:

```bash
# 현재 버전 태그 생성
git tag -a v2.0.0 -m "Release version 2.0.0"
git push origin v2.0.0

# 이전 버전 태그 확인
git tag -l
```

### 5.3 롤백 절차

#### 5.3.1 긴급 롤백 (배포 파일 교체)

**소요 시간**: 5-10분

**Step 1: 문제 확인 및 의사결정**

1. 발생한 문제의 심각도 평가
2. 롤백 결정 (담당자/관리자 승인)
3. 사용자에게 긴급 공지 발송

**Step 2: 이전 버전 파일 준비**

```bash
# 백업 폴더로 이동
cd backups/v1.1.0/

# 이전 버전 파일 확인
dir auto_fm_v1.1.0.exe
```

**Step 3: 배포 파일 교체**

**방법 A: 수동 배포**

1. 배포 서버/저장소에서 현재 버전(v2.0.0) 파일을 임시 폴더로 이동
2. 이전 버전(v1.1.0) 파일을 배포 위치에 복사
3. 파일명을 `auto_fm.exe`로 변경 (버전 번호 제거)

**방법 B: 스크립트 자동 롤백**

**rollback.bat**:
```batch
@echo off
set PREV_VERSION=1.1.0
set CURRENT_VERSION=2.0.0
set DEPLOY_PATH=\\server\shared\auto_fm
set BACKUP_PATH=backups

echo ================================================
echo      긴급 롤백: v%CURRENT_VERSION% → v%PREV_VERSION%
echo ================================================

REM 현재 버전 임시 백업
echo [1/4] 현재 버전 백업 중...
copy %DEPLOY_PATH%\auto_fm.exe %BACKUP_PATH%\rollback_backup\auto_fm_v%CURRENT_VERSION%_backup.exe

REM 이전 버전 복원
echo [2/4] 이전 버전 복원 중...
copy %BACKUP_PATH%\v%PREV_VERSION%\auto_fm_v%PREV_VERSION%.exe %DEPLOY_PATH%\auto_fm.exe

REM 파일 확인
echo [3/4] 파일 확인 중...
%DEPLOY_PATH%\auto_fm.exe --version

echo [4/4] 롤백 완료
echo ================================================
pause
```

**Step 4: 사용자 데이터 호환성 확인**

```bash
# 데이터베이스 마이그레이션이 있었던 경우
# 사용자 데이터 복구 스크립트 실행
python scripts/rollback_migration.py --from v2.0.0 --to v1.1.0
```

**Step 5: 롤백 검증**

- [ ] 이전 버전 실행 확인
- [ ] 기존 사용자 데이터 정상 로드 확인
- [ ] 주요 기능 동작 테스트
- [ ] 사용자에게 롤백 완료 공지

#### 5.3.2 단계적 롤백 (부분 롤백)

특정 사용자 그룹에만 문제가 발생하는 경우 단계적으로 롤백합니다.

**Step 1: 영향 범위 파악**

1. 문제가 발생한 사용자 환경 분석
   - Windows 버전
   - 하드웨어 사양
   - 설치 경로
2. 영향받는 사용자 목록 작성

**Step 2: 부분 배포**

1. 문제가 발생한 사용자에게만 이전 버전 제공
2. 정상 동작하는 사용자는 신규 버전 유지
3. 병렬 배포 상황 모니터링

**Step 3: 원인 분석 및 수정**

1. 문제 원인 파악
2. 수정 버전 개발 (v2.0.1)
3. 테스트 후 재배포

#### 5.3.3 소스 코드 롤백 (개발 환경)

개발 중 문제가 발생한 경우 Git을 사용하여 롤백합니다.

**방법 A: 특정 커밋으로 되돌리기**

```bash
# 이전 버전 태그 확인
git tag -l

# 이전 버전으로 체크아웃 (읽기 전용)
git checkout v1.1.0

# 새로운 브랜치 생성하여 작업
git checkout -b hotfix-v1.1.0
```

**방법 B: 특정 커밋 되돌리기 (revert)**

```bash
# 문제가 발생한 커밋 찾기
git log --oneline

# 특정 커밋 되돌리기 (새로운 커밋 생성)
git revert <commit-hash>

# 변경사항 푸시
git push origin main
```

**방법 C: 강제 리셋 (주의!)**

```bash
# 이전 커밋으로 강제 리셋 (위험!)
git reset --hard v1.1.0

# 강제 푸시 (팀원과 협의 후)
git push --force origin main
```

> **경고**: `git reset --hard`와 `git push --force`는 커밋 히스토리를 변경하므로 팀원과 충분한 협의 후 사용하세요.

### 5.4 데이터 복구

#### 5.4.1 사용자 데이터 백업

롤백 전 사용자 데이터를 백업해야 합니다:

**백업 대상**:
- `cost_calc.db`: 데이터베이스 파일
- `scenarios/*.json`: 시나리오 파일
- `logs/*.log`: 로그 파일

**백업 스크립트 (backup_user_data.bat)**:
```batch
@echo off
set USER_DATA_PATH=%APPDATA%\auto_fm
set BACKUP_PATH=user_data_backup\%DATE%

echo 사용자 데이터 백업 중...
mkdir %BACKUP_PATH%
xcopy /E /I %USER_DATA_PATH% %BACKUP_PATH%
echo 백업 완료: %BACKUP_PATH%
pause
```

#### 5.4.2 데이터베이스 마이그레이션 롤백

버전 업그레이드 시 데이터베이스 스키마가 변경된 경우:

**Step 1: 마이그레이션 히스토리 확인**

```sql
-- cost_calc.db에서 실행
SELECT * FROM migration_history ORDER BY applied_at DESC;
```

**Step 2: 롤백 스크립트 실행**

```python
# scripts/rollback_migration.py

import sqlite3
import sys

def rollback_to_version(target_version):
    """
    데이터베이스를 특정 버전으로 롤백
    """
    conn = sqlite3.connect('cost_calc.db')
    cursor = conn.cursor()

    # 현재 버전 확인
    cursor.execute("SELECT version FROM migration_history ORDER BY applied_at DESC LIMIT 1")
    current = cursor.fetchone()[0]

    print(f"Rolling back: {current} → {target_version}")

    # 롤백 SQL 실행
    if current == "2.0.0" and target_version == "1.1.0":
        # v2.0.0에서 추가된 테이블/컬럼 제거
        cursor.execute("DROP TABLE IF EXISTS new_feature_table")
        cursor.execute("ALTER TABLE job_roles DROP COLUMN new_column")

        # 롤백 기록
        cursor.execute(
            "INSERT INTO migration_history (version, action) VALUES (?, 'rollback')",
            (target_version,)
        )

    conn.commit()
    conn.close()
    print("Rollback completed successfully")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rollback_migration.py <target_version>")
        sys.exit(1)

    rollback_to_version(sys.argv[1])
```

**실행**:
```bash
python scripts/rollback_migration.py 1.1.0
```

### 5.5 롤백 후 조치

#### 5.5.1 사용자 공지

롤백 완료 후 사용자에게 공지합니다:

**공지 내용 예시**:
```
제목: [긴급] 원가산정 시스템 v2.0.0 롤백 안내

안녕하세요.

v2.0.0 배포 후 일부 환경에서 실행 오류가 발생하여
긴급히 이전 버전(v1.1.0)으로 롤백하였습니다.

▶ 조치 내용
- 배포 파일: v2.0.0 → v1.1.0 롤백
- 조치 시간: 2026-02-14 14:30
- 영향 범위: 전체 사용자

▶ 사용자 조치 사항
1. 프로그램 재시작
2. 버전 확인 (v1.1.0으로 표시되어야 함)
3. 기존 데이터 정상 로드 확인

▶ 향후 계획
- 문제 원인 분석 중
- 수정 버전(v2.0.1) 개발 예정
- 재배포 일정은 별도 공지

문의: support@example.com

감사합니다.
```

#### 5.5.2 문제 원인 분석

롤백 후 문제 원인을 철저히 분석해야 합니다:

1. **로그 분석**:
   - 오류 로그 수집 및 분석
   - 재현 시나리오 작성

2. **환경 분석**:
   - 문제 발생 환경 파악
   - 정상 동작 환경과 비교

3. **코드 리뷰**:
   - 변경된 코드 재검토
   - 테스트 케이스 보완

4. **수정 및 재배포**:
   - 수정 버전 개발
   - 철저한 테스트
   - 단계적 재배포

### 5.6 롤백 방지를 위한 베스트 프랙티스

#### 5.6.1 배포 전 검증

- [ ] 다양한 환경에서 충분한 테스트 (Windows 10, 11)
- [ ] Clean PC에서 exe 단독 실행 테스트
- [ ] 베타 테스터 그룹 운영
- [ ] 단계적 배포 (10% → 50% → 100%)

#### 5.6.2 모니터링 체계

- [ ] 배포 후 24시간 집중 모니터링
- [ ] 사용자 피드백 채널 운영
- [ ] 자동 오류 리포팅 시스템 (선택)

#### 5.6.3 문서화

- [ ] 릴리스 노트 상세 작성
- [ ] 변경사항 목록 명확히 기재
- [ ] 알려진 이슈 사전 공지
- [ ] 롤백 절차 최신화

### 5.7 롤백 체크리스트

#### 긴급 롤백 체크리스트

- [ ] 1단계: 문제 심각도 평가 및 롤백 결정
- [ ] 2단계: 이전 버전 파일 준비
- [ ] 3단계: 사용자에게 긴급 공지
- [ ] 4단계: 배포 파일 교체 (rollback.bat 실행)
- [ ] 5단계: 이전 버전 실행 확인
- [ ] 6단계: 사용자 데이터 호환성 확인
- [ ] 7단계: 롤백 완료 공지
- [ ] 8단계: 문제 원인 분석 시작

#### 데이터 롤백 체크리스트

- [ ] 1단계: 사용자 데이터 백업 (backup_user_data.bat)
- [ ] 2단계: 데이터베이스 스키마 확인
- [ ] 3단계: 마이그레이션 롤백 스크립트 실행
- [ ] 4단계: 데이터 무결성 확인
- [ ] 5단계: 사용자 데이터 복원 테스트

---

## 6. 배포 체크리스트

### 6.1 빌드 전 체크리스트

#### Phase 1: 코드 검증
- [ ] 모든 기능 정상 동작 확인
- [ ] 단위 테스트 통과 확인
- [ ] 통합 테스트 수행
- [ ] 코드 리뷰 완료
- [ ] 로그 레벨 WARNING 이상으로 설정

#### Phase 2: 버전 관리
- [ ] 버전 번호 결정 (시맨틱 버저닝)
- [ ] src/version.py 업데이트
- [ ] file_version_info.txt 업데이트
- [ ] CHANGELOG.md 업데이트
- [ ] Git 태그 생성 (`git tag v2.0.0`)

#### Phase 3: 문서 업데이트
- [ ] USER_GUIDE.md 최신화
- [ ] README.txt 작성
- [ ] INSTALL.md 확인
- [ ] DEPLOY.md (이 문서) 확인

### 6.2 빌드 체크리스트

#### Phase 1: 빌드 준비
- [ ] 이전 빌드 파일 삭제
- [ ] __pycache__ 정리
- [ ] 가상 환경 활성화
- [ ] PyInstaller 최신 버전 확인

#### Phase 2: 빌드 실행
- [ ] build.bat 또는 build.sh 실행
- [ ] 빌드 오류 없이 완료
- [ ] dist/auto_fm.exe 파일 생성 확인
- [ ] 파일 크기 확인 (50-100MB)

#### Phase 3: 실행 파일 테스트
- [ ] exe 파일 단독 실행 확인
- [ ] 초기 데이터베이스 생성 확인
- [ ] 모든 기능 정상 동작 확인
- [ ] 다른 PC에서 실행 테스트

### 6.3 배포 전 체크리스트

#### Phase 1: 패키지 구성
- [ ] 배포 폴더 생성
- [ ] auto_fm.exe 복사
- [ ] README.txt 복사
- [ ] USER_GUIDE.md 복사
- [ ] 예제 파일 포함 (선택)

#### Phase 2: 압축/설치 프로그램
- [ ] ZIP 파일 생성
- [ ] 또는 Inno Setup 설치 프로그램 생성
- [ ] 압축 파일 무결성 확인
- [ ] 파일명 버전 표기 (예: auto_fm_v2.0.zip)

#### Phase 3: 최종 테스트
- [ ] 압축 파일 압축 해제 테스트
- [ ] 설치 프로그램 설치 테스트
- [ ] 다양한 Windows 버전에서 테스트 (10, 11)
- [ ] 다양한 PC 환경에서 테스트

### 6.4 배포 후 체크리스트

#### Phase 1: 배포
- [ ] 배포 서버/저장소에 파일 업로드
- [ ] 다운로드 링크 생성
- [ ] 사용자에게 배포 공지

#### Phase 2: 모니터링
- [ ] 사용자 피드백 수집
- [ ] 버그 리포트 추적
- [ ] 사용 통계 확인 (가능한 경우)

#### Phase 3: 문서화
- [ ] 릴리스 노트 작성
- [ ] Git 저장소에 릴리스 생성
- [ ] 배포 날짜 기록

---

## 7. 문제 해결

### 7.1 빌드 오류

#### 문제 1: ModuleNotFoundError during build

```
ModuleNotFoundError: No module named 'PyQt6'
```

**원인**: 가상 환경이 활성화되지 않았거나 패키지 미설치

**해결 방법**:
```bash
# 가상 환경 활성화
venv\Scripts\activate.bat

# 패키지 재설치
pip install -r requirements.txt

# 빌드 재시도
pyinstaller auto_fm.spec
```

#### 문제 2: Failed to execute script

빌드는 성공했지만 exe 실행 시 즉시 종료

**원인**: 숨겨진 import 문제 또는 데이터 파일 누락

**해결 방법 1: 콘솔 모드로 빌드하여 오류 확인**

```bash
pyinstaller --onefile --console --name auto_fm src/main.py
```

exe 실행 시 콘솔 창에 오류 메시지 표시됨

**해결 방법 2: Hidden imports 추가**

spec 파일에 숨겨진 import 추가:

```python
a = Analysis(
    ...
    hiddenimports=['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets'],
    ...
)
```

#### 문제 3: UPX is not available

```
WARNING: UPX is not available
```

**원인**: UPX (실행 파일 압축 도구) 미설치

**해결 방법**:
1. 무시해도 빌드는 성공 (압축만 안 됨)
2. 또는 UPX 다운로드: [UPX](https://upx.github.io/)
3. UPX를 PATH에 추가

### 7.2 실행 오류

#### 문제 1: Missing DLL

```
The program can't start because api-ms-win-crt-runtime-l1-1-0.dll is missing
```

**원인**: Visual C++ Redistributable 미설치

**해결 방법**:
사용자 PC에 [Visual C++ Redistributable](https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads) 설치

#### 문제 2: Database locked

```
sqlite3.OperationalError: database is locked
```

**원인**: 다른 프로세스가 DB 파일 사용 중

**해결 방법**:
1. 모든 auto_fm.exe 인스턴스 종료
2. 작업 관리자에서 프로세스 확인 및 종료
3. 재실행

### 7.3 배포 오류

#### 문제 1: ZIP 파일 손상

다운로드 후 압축 해제 실패

**원인**: 파일 전송 중 손상

**해결 방법**:
1. 체크섬 검증 (MD5, SHA256)
2. 파일 재전송
3. 다른 압축 도구 사용 (7-Zip, WinRAR)

#### 문제 2: Windows Defender 차단

exe 실행 시 Windows Defender가 차단

**원인**: 서명되지 않은 실행 파일

**해결 방법**:
1. 코드 서명 인증서 구매 및 적용
2. 또는 사용자에게 안내:
   - "추가 정보" 클릭
   - "실행" 버튼 클릭

---

## 8. 부록

### 8.1 빌드 명령어 참조

#### 기본 빌드
```bash
# 단일 파일, GUI 모드
pyinstaller --onefile --windowed --name auto_fm src/main.py

# 폴더 기반, 콘솔 모드
pyinstaller --console --name auto_fm src/main.py
```

#### 고급 옵션
```bash
# 아이콘 + 버전 정보
pyinstaller --onefile --windowed --name auto_fm --icon=icon.ico --version-file=file_version_info.txt src/main.py

# 데이터 파일 포함
pyinstaller --onefile --windowed --name auto_fm --add-data "data;data" src/main.py

# 전체 옵션
pyinstaller --onefile --windowed --name auto_fm --icon=icon.ico --version-file=file_version_info.txt --add-data "data;data" --hidden-import=PyQt6 src/main.py
```

#### spec 파일 사용
```bash
# spec 파일 생성
pyi-makespec --onefile --windowed src/main.py

# spec 파일로 빌드
pyinstaller auto_fm.spec

# clean build
pyinstaller --clean auto_fm.spec
```

### 8.2 배포 플랫폼

#### Windows
- **파일 형식**: .exe
- **배포 방법**: ZIP, 설치 프로그램 (Inno Setup)
- **최소 OS**: Windows 10

#### macOS (참고)
- **파일 형식**: .app
- **배포 방법**: DMG
- **빌드 명령**:
  ```bash
  pyinstaller --onefile --windowed --name auto_fm src/main.py
  ```

#### Linux (참고)
- **파일 형식**: 바이너리
- **배포 방법**: tar.gz
- **빌드 명령**:
  ```bash
  pyinstaller --onefile --name auto_fm src/main.py
  ```

### 8.3 유용한 리소스

#### PyInstaller
- [PyInstaller 공식 문서](https://pyinstaller.org/en/stable/)
- [PyInstaller 옵션 목록](https://pyinstaller.org/en/stable/usage.html)
- [Hidden Imports 가이드](https://pyinstaller.org/en/stable/when-things-go-wrong.html)

#### 설치 프로그램
- [Inno Setup](https://jrsoftware.org/isinfo.php)
- [NSIS](https://nsis.sourceforge.io/)
- [WiX Toolset](https://wixtoolset.org/)

#### 코드 서명
- [Windows 코드 서명 가이드](https://docs.microsoft.com/en-us/windows-hardware/drivers/install/code-signing-best-practices)

### 8.4 배포 자동화 (CI/CD)

GitHub Actions를 사용한 자동 빌드 예시:

**.github/workflows/build.yml**:
```yaml
name: Build exe

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.12

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller

    - name: Build exe
      run: |
        pyinstaller --onefile --windowed --name auto_fm --version-file=file_version_info.txt src/main.py

    - name: Upload artifact
      uses: actions/upload-artifact@v2
      with:
        name: auto_fm.exe
        path: dist/auto_fm.exe

    - name: Create Release
      uses: softprops/action-gh-release@v1
      with:
        files: dist/auto_fm.exe
```

### 8.5 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 2.0 | 2026-02-14 | 전면 개정 (PyInstaller, 배포 자동화) |
| 1.0 | 2024-10-01 | 초판 발행 |

---

## 마치며

배포 중 문제가 발생하면:

1. 먼저 [7. 문제 해결](#7-문제-해결) 섹션을 참조하세요.
2. 빌드 로그를 확인하세요.
3. 지원이 필요한 경우 support@example.com으로 연락하세요.

**제작**: 원가산정 시스템 개발팀
**버전**: 2.0
**최종 수정일**: 2026-02-14

---

**© 2024-2026 원가산정 시스템. All rights reserved.**

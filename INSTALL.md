# 원가산정 집계 시스템 설치 가이드

> **버전**: 2.0
> **최종 수정일**: 2026-02-14
> **대상**: 개발자 및 시스템 관리자

---

## 📑 목차

1. [개요](#1-개요)
2. [시스템 요구사항](#2-시스템-요구사항)
3. [Python 환경 설정](#3-python-환경-설정)
4. [의존성 패키지 설치](#4-의존성-패키지-설치)
5. [데이터베이스 초기화](#5-데이터베이스-초기화)
6. [개발 환경 설정](#6-개발-환경-설정)
7. [실행 및 검증](#7-실행-및-검증)
8. [문제 해결](#8-문제-해결)
9. [부록](#9-부록)

---

## 1. 개요

### 1.1 설치 개요

원가산정 집계 시스템(auto_fm)은 PyQt6 기반의 데스크톱 애플리케이션으로, Python 3.12 이상 환경에서 실행됩니다.

**주요 구성 요소**:
- **Frontend**: PyQt6 (GUI)
- **Backend**: Python 3.12+
- **Database**: SQLite
- **PDF**: ReportLab
- **Excel**: openpyxl

### 1.2 설치 유형

두 가지 설치 방법을 제공합니다:

#### 방법 1: 사용자용 (.exe 파일)
- Python 설치 불필요
- 간편한 실행
- 개발 불가

#### 방법 2: 개발자용 (소스 코드)
- Python 환경 필요
- 소스 수정 가능
- 디버깅 가능

이 가이드는 **방법 2 (개발자용)**을 중심으로 설명합니다.

---

## 2. 시스템 요구사항

### 2.1 하드웨어 요구사항

#### 최소 요구사항
- **CPU**: Intel Core i3 또는 동급
- **메모리**: 4GB RAM
- **디스크**: 500MB 여유 공간
- **화면**: 1366x768 해상도

#### 권장 요구사항
- **CPU**: Intel Core i5 이상
- **메모리**: 8GB RAM 이상
- **디스크**: 2GB 여유 공간 (개발 환경 포함)
- **화면**: 1920x1080 해상도 (Full HD)

### 2.2 소프트웨어 요구사항

#### 필수 소프트웨어

| 구성 요소 | 버전 | 용도 |
|----------|------|------|
| **Python** | 3.12 이상 | 프로그램 실행 |
| **pip** | 최신 버전 | 패키지 관리 |
| **Windows** | Windows 10+ | 운영체제 |

#### 선택 소프트웨어

| 구성 요소 | 버전 | 용도 |
|----------|------|------|
| **Git** | 2.x | 버전 관리 (권장) |
| **Visual Studio Code** | 최신 | 코드 에디터 (권장) |
| **DB Browser for SQLite** | 3.x | DB 관리 도구 |

### 2.3 운영체제별 지원

| OS | 지원 여부 | 비고 |
|----|----------|------|
| Windows 10 | ✅ 완전 지원 | |
| Windows 11 | ✅ 완전 지원 | |
| macOS | ⚠️ 부분 지원 | PyQt6 호환성 확인 필요 |
| Linux | ⚠️ 부분 지원 | PyQt6 호환성 확인 필요 |

---

## 3. Python 환경 설정

### 3.1 Python 설치

#### 3.1.1 Windows에서 Python 설치

**1단계: Python 다운로드**

1. [Python 공식 웹사이트](https://www.python.org/downloads/)에 접속
2. Python 3.12 이상 버전 다운로드
3. Windows x86-64 executable installer 선택

**2단계: Python 설치**

1. 다운로드한 설치 파일 실행
2. **중요**: "Add Python to PATH" 체크박스 선택
3. "Install Now" 클릭
4. 설치 완료 대기

**3단계: 설치 확인**

```bash
python --version
```

**예상 출력**:
```
Python 3.12.1
```

**4단계: pip 확인**

```bash
pip --version
```

**예상 출력**:
```
pip 23.3.1 from C:\Users\...\Python312\lib\site-packages\pip (python 3.12)
```

#### 3.1.2 Python PATH 설정 (수동)

"Add Python to PATH"를 선택하지 않았다면 수동으로 설정:

**Windows 10/11**:

1. **시작** → **시스템 환경 변수 편집** 검색
2. **환경 변수** 버튼 클릭
3. **시스템 변수**에서 **Path** 선택 → **편집**
4. **새로 만들기** → 다음 경로 추가:
   ```
   C:\Users\[사용자명]\AppData\Local\Programs\Python\Python312\
   C:\Users\[사용자명]\AppData\Local\Programs\Python\Python312\Scripts\
   ```
5. **확인** 클릭
6. 새 터미널에서 `python --version` 확인

### 3.2 가상 환경 설정 (권장)

가상 환경을 사용하면 프로젝트별로 독립적인 Python 환경을 구성할 수 있습니다.

#### 3.2.1 venv를 사용한 가상 환경 생성

**1단계: 프로젝트 폴더로 이동**

```bash
cd C:\Users\[사용자명]\Documents\auto_fm\auto_fm
```

**2단계: 가상 환경 생성**

```bash
python -m venv venv
```

이 명령은 `venv` 폴더를 생성하고 독립적인 Python 환경을 구성합니다.

**3단계: 가상 환경 활성화**

**Windows Command Prompt**:
```bash
venv\Scripts\activate.bat
```

**Windows PowerShell**:
```powershell
venv\Scripts\Activate.ps1
```

**Git Bash**:
```bash
source venv/Scripts/activate
```

**활성화 확인**:
```bash
(venv) C:\Users\...\auto_fm>
```

프롬프트 앞에 `(venv)`가 표시되면 성공입니다.

**4단계: 가상 환경 비활성화 (필요시)**

```bash
deactivate
```

#### 3.2.2 conda를 사용한 가상 환경 (선택)

Anaconda가 설치되어 있는 경우:

**가상 환경 생성**:
```bash
conda create -n auto_fm python=3.12
```

**가상 환경 활성화**:
```bash
conda activate auto_fm
```

**가상 환경 비활성화**:
```bash
conda deactivate
```

---

## 4. 의존성 패키지 설치

### 4.1 requirements.txt 개요

프로젝트의 모든 의존성 패키지는 `requirements.txt` 파일에 정의되어 있습니다.

**requirements.txt 내용**:
```
PyQt6>=6.6.0
Pillow>=10.0.0
reportlab>=4.0.0
openpyxl>=3.0.0
```

### 4.2 패키지 일괄 설치

#### 4.2.1 기본 설치

가상 환경이 활성화된 상태에서:

```bash
pip install -r requirements.txt
```

**설치 진행 화면**:
```
Collecting PyQt6>=6.6.0
  Downloading PyQt6-6.6.1-...
Collecting Pillow>=10.0.0
  Downloading Pillow-10.2.0-...
...
Successfully installed PyQt6-6.6.1 Pillow-10.2.0 reportlab-4.0.9 openpyxl-3.1.2
```

#### 4.2.2 특정 버전 설치

특정 버전이 필요한 경우:

```bash
pip install PyQt6==6.6.1
pip install Pillow==10.2.0
pip install reportlab==4.0.9
pip install openpyxl==3.1.2
```

#### 4.2.3 업그레이드 설치

기존 패키지를 최신 버전으로 업그레이드:

```bash
pip install -r requirements.txt --upgrade
```

### 4.3 개별 패키지 설명

#### 4.3.1 PyQt6

**용도**: GUI 프레임워크
**크기**: ~50MB
**설치 시간**: 1-2분

**수동 설치**:
```bash
pip install PyQt6
```

**확인**:
```bash
python -c "import PyQt6; print(PyQt6.__version__)"
```

#### 4.3.2 Pillow

**용도**: 이미지 처리
**크기**: ~3MB
**설치 시간**: 30초

**수동 설치**:
```bash
pip install Pillow
```

**확인**:
```bash
python -c "from PIL import Image; print(Image.__version__)"
```

#### 4.3.3 ReportLab

**용도**: PDF 생성
**크기**: ~2MB
**설치 시간**: 30초

**수동 설치**:
```bash
pip install reportlab
```

**확인**:
```bash
python -c "import reportlab; print(reportlab.Version)"
```

#### 4.3.4 openpyxl

**용도**: Excel 파일 처리
**크기**: ~1MB
**설치 시간**: 20초

**수동 설치**:
```bash
pip install openpyxl
```

**확인**:
```bash
python -c "import openpyxl; print(openpyxl.__version__)"
```

### 4.4 설치 확인

모든 패키지가 올바르게 설치되었는지 확인:

```bash
pip list
```

**예상 출력**:
```
Package    Version
---------- -------
openpyxl   3.1.2
Pillow     10.2.0
PyQt6      6.6.1
reportlab  4.0.9
```

**또는** 설치된 패키지를 requirements.txt 형식으로 저장:

```bash
pip freeze > installed_packages.txt
```

---

## 5. 데이터베이스 초기화

### 5.1 SQLite 데이터베이스 개요

원가산정 시스템은 SQLite를 사용하여 다음 데이터를 저장합니다:

- 직무별 임금 데이터 (wages_master 테이블)
- 경비 항목 데이터 (expense_items, expense_sub_items 테이블)
- 사용자 정의 직무 데이터

### 5.2 자동 초기화

프로그램을 처음 실행하면 자동으로:

1. `cost_calc.db` 파일 생성
2. 필요한 테이블 생성
3. 마이그레이션 파일 실행
4. 초기 데이터 로딩

**데이터베이스 파일 위치**:
```
C:\Users\[사용자명]\Documents\auto_fm\auto_fm\cost_calc.db
```

### 5.3 수동 초기화 (필요시)

자동 초기화가 실패한 경우 수동으로 초기화:

#### 5.3.1 기존 DB 삭제 (선택)

```bash
# Windows Command Prompt
del cost_calc.db

# PowerShell
Remove-Item cost_calc.db

# Git Bash
rm cost_calc.db
```

#### 5.3.2 프로그램 실행하여 DB 생성

```bash
python -m src.main
```

프로그램이 시작되면서 자동으로 데이터베이스가 생성됩니다.

### 5.4 데이터베이스 구조 확인

#### 5.4.1 DB Browser for SQLite 사용

1. [DB Browser for SQLite](https://sqlitebrowser.org/) 다운로드 및 설치
2. `cost_calc.db` 파일 열기
3. "Database Structure" 탭에서 테이블 구조 확인

#### 5.4.2 Python으로 확인

```python
import sqlite3

conn = sqlite3.connect('cost_calc.db')
cursor = conn.cursor()

# 테이블 목록 확인
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())

# wages_master 테이블 구조 확인
cursor.execute("PRAGMA table_info(wages_master);")
print(cursor.fetchall())

conn.close()
```

**예상 출력**:
```
[('migrations',), ('wages_master',), ('expense_items',), ('expense_sub_items',)]
[(0, 'id', 'INTEGER', 0, None, 1), (1, 'scenario_id', 'TEXT', 1, None, 0), ...]
```

### 5.5 초기 데이터 확인

#### 5.5.1 임금 데이터 확인

```python
import sqlite3

conn = sqlite3.connect('cost_calc.db')
cursor = conn.cursor()

# 2024년 기준 직무 조회
cursor.execute("""
    SELECT job_code, job_name, grade, daily_wage
    FROM wages_master
    WHERE scenario_id = 'year_2024'
    LIMIT 10
""")

for row in cursor.fetchall():
    print(row)

conn.close()
```

**예상 출력**:
```
(10100, '시설관리원', '1급', 110000.0)
(10101, '시설관리원', '2급', 105000.0)
(10200, '미화원', '1급', 95000.0)
...
```

#### 5.5.2 경비 항목 확인

```python
import sqlite3

conn = sqlite3.connect('cost_calc.db')
cursor = conn.cursor()

# 경비 항목 조회
cursor.execute("SELECT item_name, group_name FROM expense_items LIMIT 5")

for row in cursor.fetchall():
    print(row)

conn.close()
```

**예상 출력**:
```
('차량유지비', '운영비')
('피복비', '운영비')
('통신비', '운영비')
...
```

---

## 6. 개발 환경 설정

### 6.1 코드 에디터 설정

#### 6.1.1 Visual Studio Code 설정

**1단계: VS Code 설치**

1. [Visual Studio Code](https://code.visualstudio.com/) 다운로드
2. 설치 및 실행

**2단계: Python 확장 설치**

1. 확장(Extensions) 패널 열기 (Ctrl+Shift+X)
2. "Python" 검색
3. Microsoft의 Python 확장 설치

**3단계: 프로젝트 폴더 열기**

1. File → Open Folder
2. `auto_fm` 폴더 선택

**4단계: Python 인터프리터 선택**

1. Ctrl+Shift+P → "Python: Select Interpreter"
2. 가상 환경 경로 선택: `.\venv\Scripts\python.exe`

**5단계: settings.json 설정**

`.vscode/settings.json` 파일 생성:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}\\venv\\Scripts\\python.exe",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
}
```

#### 6.1.2 PyCharm 설정 (선택)

**1단계: PyCharm 설치**

1. [PyCharm Community Edition](https://www.jetbrains.com/pycharm/download/) 다운로드
2. 설치 및 실행

**2단계: 프로젝트 열기**

1. File → Open
2. `auto_fm` 폴더 선택

**3단계: Python 인터프리터 설정**

1. File → Settings → Project → Python Interpreter
2. "Add Interpreter" → "Existing environment"
3. 가상 환경 경로 선택: `.\venv\Scripts\python.exe`

### 6.2 Git 설정 (권장)

#### 6.2.1 Git 설치

1. [Git for Windows](https://git-scm.com/download/win) 다운로드
2. 설치 (기본 설정 사용)

#### 6.2.2 Git 초기화 (신규 프로젝트)

```bash
cd C:\Users\[사용자명]\Documents\auto_fm\auto_fm
git init
```

#### 6.2.3 .gitignore 설정

`.gitignore` 파일 생성:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Database
*.db
*.sqlite

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Build
build/
dist/
*.spec

# User data
scenarios/
```

#### 6.2.4 첫 커밋

```bash
git add .
git commit -m "Initial commit"
```

### 6.3 디버깅 설정

#### 6.3.1 VS Code 디버깅

`.vscode/launch.json` 파일 생성:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Main",
            "type": "python",
            "request": "launch",
            "module": "src.main",
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
```

**디버깅 실행**:
1. F5 키 누르기
2. 또는 Run → Start Debugging

#### 6.3.2 로깅 설정

`logging_config.py` 확인:

```python
import logging
import os

def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "app.log"), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
```

로그 파일 위치: `logs/app.log`

---

## 7. 실행 및 검증

### 7.1 프로그램 실행

#### 7.1.1 명령줄에서 실행

**Windows Command Prompt**:
```bash
cd C:\Users\[사용자명]\Documents\auto_fm\auto_fm
python -m src.main
```

**PowerShell**:
```powershell
cd C:\Users\[사용자명]\Documents\auto_fm\auto_fm
python -m src.main
```

**Git Bash**:
```bash
cd /c/Users/[사용자명]/Documents/auto_fm/auto_fm
python -m src.main
```

#### 7.1.2 VS Code에서 실행

1. `src/main.py` 파일 열기
2. F5 키 또는 Run → Start Debugging

#### 7.1.3 실행 스크립트 생성 (편의용)

`run.bat` 파일 생성:

```batch
@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
python -m src.main
pause
```

실행: `run.bat` 더블클릭

### 7.2 정상 동작 확인

#### 7.2.1 콘솔 출력 확인

정상 실행 시 다음과 유사한 메시지가 출력됩니다:

```
INFO:root:Starting auto_fm cost calculator
INFO:root:Database initialized
INFO:root:Migrations completed
INFO:root:Master data loaded: 50 jobs, 20 expense items
INFO:root:Main window created
```

#### 7.2.2 GUI 확인

프로그램 창이 나타나고 다음을 확인:

- ✅ 창이 정상적으로 표시됨
- ✅ 메뉴 바가 보임
- ✅ 탭 (직무별 인원입력, 경비 입력, 비교) 표시됨
- ✅ 기준년도 드롭다운 작동

#### 7.2.3 기능 테스트

**테스트 1: 직무 선택**
1. "직무별 인원입력" 탭 선택
2. 빈 행의 "직무코드" 드롭다운 클릭
3. 직무 목록이 표시되는지 확인

**테스트 2: 데이터 입력**
1. 직무 선택: 시설관리원 1급
2. 인원: 2
3. 자동 계산 확인

**테스트 3: 집계 실행**
1. "집계 실행" 버튼 클릭
2. 결과가 우측 패널에 표시되는지 확인

### 7.3 성능 확인

#### 7.3.1 시작 시간

정상적인 시작 시간: 2-3초 이내

**측정 방법**:
```bash
python -m timeit -n 1 -r 1 -s "import subprocess" "subprocess.run(['python', '-m', 'src.main'])"
```

#### 7.3.2 메모리 사용량

정상적인 메모리 사용량: 50-100MB

**Windows Task Manager 확인**:
1. Ctrl+Shift+Esc
2. "Details" 탭
3. python.exe 프로세스 확인

---

## 8. 문제 해결

### 8.1 Python 설치 오류

#### 문제 1: python 명령을 찾을 수 없음

```
'python' is not recognized as an internal or external command
```

**해결 방법**:
1. Python이 PATH에 추가되었는지 확인
2. 재설치 시 "Add Python to PATH" 체크
3. 수동으로 PATH 설정 ([3.1.2절](#312-python-path-설정-수동) 참조)

#### 문제 2: Python 버전 불일치

```
This application requires Python 3.12 or higher
```

**해결 방법**:
1. 현재 버전 확인: `python --version`
2. Python 3.12+ 설치
3. 가상 환경 재생성

### 8.2 패키지 설치 오류

#### 문제 1: pip 업그레이드 경고

```
WARNING: You are using pip version XX.X; however, version YY.Y is available.
```

**해결 방법**:
```bash
python -m pip install --upgrade pip
```

#### 문제 2: PyQt6 설치 실패

```
ERROR: Could not build wheels for PyQt6
```

**해결 방법**:
1. Visual C++ Build Tools 설치
2. 또는 사전 빌드된 wheel 파일 사용:
   ```bash
   pip install PyQt6 --only-binary :all:
   ```

#### 문제 3: 네트워크 오류

```
ERROR: Could not find a version that satisfies the requirement PyQt6
```

**해결 방법**:
1. 인터넷 연결 확인
2. 프록시 설정:
   ```bash
   pip install --proxy http://user:password@proxy:port -r requirements.txt
   ```
3. 오프라인 설치 (wheel 파일 사전 다운로드)

### 8.3 데이터베이스 오류

#### 문제 1: 데이터베이스 파일 생성 실패

```
sqlite3.OperationalError: unable to open database file
```

**해결 방법**:
1. 폴더 쓰기 권한 확인
2. 관리자 권한으로 실행
3. 다른 위치로 프로젝트 폴더 이동

#### 문제 2: 마이그레이션 오류

```
ERROR: Migration failed: table wages_master already exists
```

**해결 방법**:
1. `cost_calc.db` 파일 삭제
2. 프로그램 재실행
3. 자동으로 새 데이터베이스 생성됨

### 8.4 실행 오류

#### 문제 1: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'PyQt6'
```

**해결 방법**:
1. 가상 환경 활성화 확인
2. 패키지 재설치:
   ```bash
   pip install -r requirements.txt
   ```

#### 문제 2: ImportError

```
ImportError: DLL load failed while importing QtCore
```

**해결 방법**:
1. Visual C++ Redistributable 설치
2. PyQt6 재설치:
   ```bash
   pip uninstall PyQt6
   pip install PyQt6
   ```

#### 문제 3: 빈 화면 표시

GUI 창은 나타나지만 내용이 없음

**해결 방법**:
1. 로그 파일 확인: `logs/app.log`
2. 콘솔 오류 메시지 확인
3. 데이터베이스 파일 재생성

### 8.5 성능 문제

#### 문제 1: 시작 시간 느림 (5초 이상)

**해결 방법**:
1. SSD 사용 권장
2. 백그라운드 프로세스 확인
3. 데이터베이스 파일 크기 확인

#### 문제 2: 메모리 사용량 과다 (200MB 이상)

**해결 방법**:
1. 다른 프로그램 종료
2. 로그 파일 크기 확인 및 삭제
3. 시나리오 데이터 정리

---

## 9. 부록

### 9.1 전체 설치 체크리스트

#### Phase 1: 준비
- [ ] Python 3.12+ 설치 확인
- [ ] pip 최신 버전 확인
- [ ] Git 설치 (선택)
- [ ] VS Code 설치 (선택)

#### Phase 2: 프로젝트 설정
- [ ] 프로젝트 폴더 생성/복사
- [ ] 가상 환경 생성
- [ ] 가상 환경 활성화
- [ ] requirements.txt 확인

#### Phase 3: 패키지 설치
- [ ] PyQt6 설치
- [ ] Pillow 설치
- [ ] reportlab 설치
- [ ] openpyxl 설치
- [ ] 설치 확인 (`pip list`)

#### Phase 4: 데이터베이스
- [ ] 프로그램 첫 실행
- [ ] cost_calc.db 파일 생성 확인
- [ ] 임금 데이터 로딩 확인
- [ ] 경비 항목 로딩 확인

#### Phase 5: 검증
- [ ] GUI 정상 표시
- [ ] 직무 선택 기능 확인
- [ ] 데이터 입력 기능 확인
- [ ] 집계 실행 기능 확인
- [ ] 결과 표시 확인

### 9.2 명령어 빠른 참조

#### Python 관련
```bash
# Python 버전 확인
python --version

# pip 업그레이드
python -m pip install --upgrade pip

# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화 (Windows)
venv\Scripts\activate.bat

# 가상 환경 비활성화
deactivate
```

#### 패키지 관리
```bash
# 패키지 설치
pip install -r requirements.txt

# 패키지 목록 확인
pip list

# 설치된 패키지 저장
pip freeze > installed_packages.txt

# 특정 패키지 제거
pip uninstall PyQt6
```

#### 프로그램 실행
```bash
# 표준 실행
python -m src.main

# 디버그 모드
python -m pdb src/main.py

# 로그 레벨 설정
set LOG_LEVEL=DEBUG && python -m src.main
```

### 9.3 디렉토리 구조

```
auto_fm/
├── src/
│   ├── __init__.py
│   ├── main.py                 # 메인 진입점
│   ├── domain/                 # 비즈니스 로직
│   │   ├── calculator/         # 계산 로직
│   │   ├── context/            # 계산 컨텍스트
│   │   ├── masterdata/         # 마스터 데이터
│   │   └── migrations/         # DB 마이그레이션
│   └── ui/                     # UI 컴포넌트
│       ├── main_window.py
│       ├── job_role_table.py
│       ├── expense_input_table.py
│       └── compare/
├── data/                       # 데이터 파일
│   └── wages_master.json
├── logs/                       # 로그 파일
│   └── app.log
├── venv/                       # 가상 환경 (생성됨)
├── cost_calc.db               # 데이터베이스 (생성됨)
├── requirements.txt            # 의존성 목록
├── USER_GUIDE.md              # 사용자 가이드
└── INSTALL.md                 # 이 파일
```

### 9.4 유용한 리소스

#### 공식 문서
- [Python 공식 문서](https://docs.python.org/3/)
- [PyQt6 공식 문서](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [SQLite 문서](https://www.sqlite.org/docs.html)

#### 튜토리얼
- [Python 가상 환경 가이드](https://docs.python.org/3/tutorial/venv.html)
- [PyQt6 튜토리얼](https://www.pythonguis.com/pyqt6-tutorial/)

#### 도구
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- [Visual Studio Code](https://code.visualstudio.com/)
- [PyCharm](https://www.jetbrains.com/pycharm/)

### 9.5 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 2.0 | 2026-02-14 | 전면 개정 (가상 환경, 상세 설명 추가) |
| 1.0 | 2024-10-01 | 초판 발행 |

---

## 마치며

설치 중 문제가 발생하면:

1. 먼저 [8. 문제 해결](#8-문제-해결) 섹션을 참조하세요.
2. 로그 파일(`logs/app.log`)을 확인하세요.
3. 지원이 필요한 경우 support@example.com으로 연락하세요.

**제작**: 원가산정 시스템 개발팀
**버전**: 2.0
**최종 수정일**: 2026-02-14

---

**© 2024-2026 원가산정 시스템. All rights reserved.**

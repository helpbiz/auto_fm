# Design: App Stability & User Manual

> **Feature ID**: app-stability-and-user-manual
> **Plan Document**: [app-stability-and-user-manual.plan.md](../../01-plan/features/app-stability-and-user-manual.plan.md)
> **Created**: 2026-02-14
> **Status**: Design
> **Version**: 1.0

---

## 📐 Design Overview

This design document specifies the structure, content, and implementation approach for creating comprehensive user documentation for the 원가산정 집계 시스템 (auto_fm).

### Goals
1. ✅ Verify app stability (complete - no errors found)
2. 📄 Create user-friendly Korean manual
3. 📸 Include visual guides and screenshots
4. 🔧 Provide installation and deployment guides

---

## 📚 Document Structure

### 1. USER_GUIDE.md (사용자 매뉴얼)

#### Document Metadata
```yaml
Document: USER_GUIDE.md
Language: Korean (한글)
Target Audience: Non-technical end users
Format: Markdown with screenshots
Location: ./USER_GUIDE.md (project root)
Estimated Length: 3000-4000 lines
```

#### Table of Contents Structure
```markdown
# 원가산정 집계 시스템 사용자 매뉴얼

## 목차
1. 시작하기
   1.1 시스템 요구사항
   1.2 프로그램 실행 방법
   1.3 화면 구성 개요

2. 기본 개념
   2.1 원가 계산이란?
   2.2 시나리오의 개념
   2.3 주요 용어 설명

3. 기준 설정
   3.1 기준년도 선택
   3.2 월 근무일수 설정
   3.3 일 근무시간 설정

4. 직무별 인원 입력
   4.1 직무 선택하기
   4.2 인원 수 입력하기
   4.3 근무조건 설정하기
   4.4 비고 작성하기

5. 경비 입력
   5.1 경비 항목 이해하기
   5.2 고정경비 입력
   5.3 변동경비 입력
   5.4 대행비 입력

6. 집계 및 결과 확인
   6.1 집계 실행하기
   6.2 요약 결과 보기
   6.3 노무비 상세 확인
   6.4 경비 상세 확인

7. 시나리오 관리
   7.1 시나리오 저장하기
   7.2 시나리오 불러오기
   7.3 시나리오 비교하기
   7.4 JSON 파일로 저장하기

8. 데이터 내보내기
   8.1 PDF로 요약 내보내기
   8.2 Excel로 상세 내보내기
   8.3 내보낸 파일 활용하기

9. 고급 기능
   9.1 전년 대비 비교
   9.2 일반관리비/이윤 조정
   9.3 사용자 정의 직무 추가

10. 문제 해결
    10.1 자주 묻는 질문 (FAQ)
    10.2 오류 메시지 해결
    10.3 데이터 복구 방법

11. 부록
    11.1 용어 사전
    11.2 단축키 목록
    11.3 지원 및 문의
```

#### Content Specifications

##### Section 1: 시작하기
**Length**: ~300 lines
**Screenshots**: 3개
- Screenshot 1: 프로그램 실행 화면
- Screenshot 2: 메인 화면 전체 구성
- Screenshot 3: 메뉴바 및 버튼 설명

**Content Details**:
```markdown
### 1.1 시스템 요구사항

#### 필수 요구사항
- 운영체제: Windows 10 이상
- Python: 3.12 이상 (exe 버전은 불필요)
- 메모리: 4GB RAM 이상 권장
- 디스크 공간: 100MB 이상

#### 권장 사양
- 화면 해상도: 1920x1080 이상
- Python 가상환경 사용 권장 (개발자용)

### 1.2 프로그램 실행 방법

#### 방법 1: EXE 파일 실행 (일반 사용자)
1. `auto_fm.exe` 파일을 더블클릭합니다
2. Windows Defender 경고가 나타나면 "추가 정보" → "실행" 클릭
3. 프로그램이 시작됩니다

#### 방법 2: Python으로 실행 (개발자)
```bash
# 가상환경 활성화
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 프로그램 실행
python -m src.main
```

[Screenshot: 실행 화면]

### 1.3 화면 구성 개요

프로그램 화면은 크게 3개 영역으로 구성됩니다:

1. **좌측 패널**: 시나리오명 입력
2. **중앙 탭**: 데이터 입력 및 결과 확인
   - 기준년도
   - 직무별 인원입력
   - 경비 입력
   - 요약
   - 노무비 상세
   - 경비 상세
   - 시나리오 비교
3. **우측 차트**: 비용 구성 도넛 차트

[Screenshot: 화면 구성 설명 (라벨 포함)]
```

##### Section 2: 기본 개념
**Length**: ~200 lines
**Screenshots**: 1개
**Diagrams**: 2개 (개념도)

```markdown
### 2.1 원가 계산이란?

원가 계산은 특정 프로젝트나 서비스를 수행하는 데 필요한
총 비용을 계산하는 과정입니다.

본 시스템에서는 다음 항목들을 계산합니다:
- 노무비 (인건비)
- 경비 (고정/변동/대행비)
- 일반관리비
- 이윤

최종 결과 = 노무비 + 경비 + 일반관리비 + 이윤

[Diagram: 원가 구성 요소]

### 2.2 시나리오의 개념

"시나리오"는 하나의 견적 또는 계산 케이스를 의미합니다.

예:
- 시나리오 A: 2024년 기준, 인원 10명
- 시나리오 B: 2025년 기준, 인원 15명

여러 시나리오를 저장하고 비교할 수 있습니다.

### 2.3 주요 용어 설명

| 용어 | 설명 | 예시 |
|------|------|------|
| 직무 | 업무 역할 구분 | 시설관리원, 경비원, 미화원 |
| 인원 | 해당 직무에 투입되는 사람 수 | 5명 |
| 노임단가 | 1인 1일 기준 급여 | 120,000원 |
| 근무일수 | 월 근무일수 | 20.6일 |
| 고정경비 | 인원과 무관한 경비 | 산재보험료, 국민연금 |
| 변동경비 | 인원/사용량에 비례 | 피복비, 복리후생비 |
| 일반관리비 | 회사 운영비 비율 | 총액의 5% |
| 이윤 | 회사 이익 비율 | 총액의 10% |
```

##### Section 3-8: 핵심 기능 상세
**Total Length**: ~2000 lines
**Screenshots**: 10-12개
**Each section**: 250-300 lines

**Screenshot List**:
1. 기준년도 선택 화면
2. 직무 선택 ComboBox
3. 인원 입력 테이블 (filled data)
4. 경비 입력 화면 (고정경비)
5. 경비 입력 화면 (변동경비)
6. 집계 실행 버튼
7. 요약 결과 화면
8. 노무비 상세 테이블
9. 경비 상세 테이블
10. 시나리오 비교 화면
11. PDF 내보내기 다이얼로그
12. Excel 파일 열기 예시

**Content Pattern (Each Feature)**:
```markdown
### X.Y 기능명

#### 개요
[기능에 대한 간단한 설명]

#### 사용 방법
**Step 1**: [첫 번째 단계]
[Screenshot if needed]

**Step 2**: [두 번째 단계]
[Screenshot if needed]

**Step 3**: [세 번째 단계]

#### 주의사항
- 주의할 점 1
- 주의할 점 2

#### 예제
[실제 사용 예제 with 스크린샷]

#### Tip 💡
[유용한 팁]
```

##### Section 9: 고급 기능
**Length**: ~300 lines
**Screenshots**: 2개

```markdown
### 9.1 전년 대비 비교

전년도 데이터와 현재 계산 결과를 비교할 수 있습니다.

#### 사용 방법
1. 집계 실행 후 "전년 기준으로 저장" 버튼 클릭
2. 다음 계산 시 자동으로 전년 대비 증감액 표시

[Screenshot: 전년 대비 표시 예시]

### 9.2 일반관리비/이윤 조정

기본값은 5%/10%이지만 조정 가능합니다.

#### 조정 방법
1. "설정" 메뉴 클릭
2. 일반관리비/이윤 비율 입력
3. 저장 후 재집계

### 9.3 사용자 정의 직무 추가

표준 직무 외에 사용자 정의 직무를 추가할 수 있습니다.

#### 추가 방법
[상세 절차]
```

##### Section 10: 문제 해결
**Length**: ~400 lines
**Format**: FAQ style

```markdown
### 10.1 자주 묻는 질문 (FAQ)

#### Q1: 프로그램이 실행되지 않아요
A: 다음을 확인해주세요:
- Python 3.12 이상 설치 확인
- 필요한 패키지 설치 확인 (`pip install -r requirements.txt`)
- 관리자 권한으로 실행

#### Q2: 계산 결과가 0원으로 나와요
A: 다음을 확인해주세요:
- 인원 수가 입력되었는지 확인
- 기준년도가 선택되었는지 확인
- 마스터 데이터가 로드되었는지 확인

#### Q3: 저장한 시나리오를 불러올 수 없어요
A: 파일 경로와 파일명을 확인해주세요.
시나리오는 `scenarios/` 폴더에 저장됩니다.

[... 10-15개 FAQ items]

### 10.2 오류 메시지 해결

#### "ModuleNotFoundError: No module named 'PyQt6'"
**원인**: PyQt6 패키지가 설치되지 않음
**해결**: `pip install PyQt6` 실행

#### "Database connection failed"
**원인**: 데이터베이스 파일 손상
**해결**: `cost_calc.db` 파일 삭제 후 재실행

[... more error messages]

### 10.3 데이터 복구 방법

시나리오 데이터가 손실된 경우:
1. `scenarios/` 폴더 확인
2. JSON 파일 백업 확인
3. 최근 저장 파일 복원
```

##### Section 11: 부록
**Length**: ~200 lines

```markdown
### 11.1 용어 사전

[Full glossary of terms]

### 11.2 단축키 목록

| 단축키 | 기능 |
|--------|------|
| Ctrl+S | 시나리오 저장 |
| Ctrl+O | 시나리오 불러오기 |
| Ctrl+E | Excel 내보내기 |
| F5 | 집계 실행 |
| F1 | 도움말 |

### 11.3 지원 및 문의

- **개발자**: Development Team
- **이메일**: support@example.com
- **GitHub**: https://github.com/your-repo/auto_fm
- **문서 버전**: 1.0 (2026-02-14)
```

---

### 2. INSTALL.md (설치 가이드)

#### Document Metadata
```yaml
Document: INSTALL.md
Language: Korean/English
Target Audience: Technical users, system administrators
Format: Markdown
Location: ./INSTALL.md
Estimated Length: 500-700 lines
```

#### Structure
```markdown
# 원가산정 집계 시스템 설치 가이드
# Installation Guide

## 목차 / Table of Contents

1. 시스템 요구사항 / System Requirements
2. Python 환경 설정 / Python Environment Setup
3. 의존성 패키지 설치 / Dependencies Installation
4. 데이터베이스 초기화 / Database Initialization
5. 첫 실행 / First Run
6. 문제 해결 / Troubleshooting

---

## 1. 시스템 요구사항 / System Requirements

### 최소 요구사항 / Minimum Requirements
- OS: Windows 10, macOS 10.15+, Ubuntu 20.04+
- Python: 3.12 or higher
- RAM: 4GB
- Disk: 100MB

### 권장 사양 / Recommended
- RAM: 8GB+
- Python: 3.12+
- Virtual Environment 사용 / Use Virtual Environment

---

## 2. Python 환경 설정 / Python Environment Setup

### Windows
```bash
# Python 설치 확인
python --version

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
venv\Scripts\activate
```

### macOS / Linux
```bash
# Python 설치 확인
python3 --version

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate
```

---

## 3. 의존성 패키지 설치 / Dependencies Installation

### 자동 설치 / Automatic Installation
```bash
# 모든 패키지 설치
pip install -r requirements.txt
```

### 수동 설치 / Manual Installation
```bash
# 개별 패키지 설치
pip install PyQt6>=6.0.0
pip install Pillow>=10.0.0
pip install reportlab>=4.0.0
pip install openpyxl>=3.0.0
```

### 의존성 목록 / Dependency List
- PyQt6: GUI framework
- Pillow: Image processing
- reportlab: PDF generation
- openpyxl: Excel file handling

---

## 4. 데이터베이스 초기화 / Database Initialization

데이터베이스는 첫 실행 시 자동으로 생성됩니다.
The database is automatically created on first run.

### 수동 초기화 (필요시) / Manual Initialization (if needed)
```bash
# 기존 DB 삭제 (주의!)
# Delete existing DB (caution!)
rm cost_calc.db

# 재생성
# Recreate
python -m src.main
```

### 마스터 데이터 확인 / Verify Master Data
```bash
sqlite3 cost_calc.db
.tables
SELECT COUNT(*) FROM job_roles;
.quit
```

---

## 5. 첫 실행 / First Run

### 실행 방법 / How to Run
```bash
# 가상환경 활성화 (필수)
# Activate virtual environment (required)
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 프로그램 실행
# Run the program
python -m src.main
```

### 실행 확인 / Verify Installation
- GUI 창이 나타나는지 확인
- 탭이 정상적으로 로드되는지 확인
- 경고 메시지는 정상 (WARNING은 무시 가능)

---

## 6. 문제 해결 / Troubleshooting

### ModuleNotFoundError
```bash
# 패키지 재설치
pip install -r requirements.txt --force-reinstall
```

### Qt Platform Plugin Error
```bash
# Windows
set QT_QPA_PLATFORM_PLUGIN_PATH=venv\Lib\site-packages\PyQt6\Qt6\plugins

# macOS/Linux
export QT_QPA_PLATFORM_PLUGIN_PATH=venv/lib/python3.12/site-packages/PyQt6/Qt6/plugins
```

### Database Locked Error
```bash
# 다른 프로세스가 DB 사용 중
# Close all instances and retry
pkill -f "python -m src.main"
```

---

## 부록: 개발 환경 설정 / Appendix: Development Setup

### 개발 의존성 설치 / Install Dev Dependencies
```bash
pip install -r requirements-dev.txt
```

### 테스트 실행 / Run Tests
```bash
pytest tests/
```

### 코드 스타일 검사 / Code Style Check
```bash
black src/
flake8 src/
```
```

---

### 3. DEPLOY.md (배포 가이드)

#### Document Metadata
```yaml
Document: DEPLOY.md
Language: Korean/English
Target Audience: Developers, Release managers
Format: Markdown
Location: ./DEPLOY.md
Estimated Length: 600-800 lines
```

#### Structure
```markdown
# 배포 가이드 / Deployment Guide

## 목차 / Table of Contents

1. EXE 빌드 / Build EXE
2. 배포 체크리스트 / Deployment Checklist
3. 인스톨러 생성 / Create Installer
4. 업데이트 배포 / Deploy Updates
5. 롤백 절차 / Rollback Procedure

---

## 1. EXE 빌드 / Build EXE

### PyInstaller 설치
```bash
pip install pyinstaller
```

### 빌드 명령
```bash
# 단일 파일 EXE 생성
pyinstaller --onefile --windowed \
  --name="원가산정" \
  --icon=icon.ico \
  --add-data="data:data" \
  src/main.py
```

### 빌드 스크립트 (build.bat)
```batch
@echo off
echo ========================================
echo  원가산정 집계 시스템 빌드
echo ========================================

REM 가상환경 활성화
call venv\Scripts\activate

REM 이전 빌드 삭제
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM PyInstaller 실행
pyinstaller auto_fm.spec

echo.
echo 빌드 완료: dist\원가산정.exe
echo.
pause
```

### 빌드 확인
1. `dist/원가산정.exe` 파일 확인
2. 테스트 실행
3. 바이러스 검사 (Windows Defender)

---

## 2. 배포 체크리스트 / Deployment Checklist

### 빌드 전 체크리스트
- [ ] 모든 테스트 통과 확인
- [ ] 버전 번호 업데이트 (`src/version.py`)
- [ ] CHANGELOG.md 업데이트
- [ ] 데이터베이스 마이그레이션 확인
- [ ] requirements.txt 업데이트
- [ ] 문서 업데이트 (USER_GUIDE.md)

### 빌드 후 체크리스트
- [ ] EXE 파일 생성 확인
- [ ] EXE 실행 테스트 (Clean PC)
- [ ] 바이러스 스캔 통과
- [ ] 파일 크기 확인 (< 100MB)
- [ ] 코드 서명 (선택사항)

### 배포 전 체크리스트
- [ ] 릴리스 노트 작성
- [ ] 백업 생성
- [ ] 다운로드 링크 테스트
- [ ] 사용자 공지사항 작성

---

## 3. 인스톨러 생성 / Create Installer

### Inno Setup 사용
```iss
[Setup]
AppName=원가산정 집계 시스템
AppVersion=1.0.0
DefaultDirName={pf}\AutoFM
DefaultGroupName=AutoFM
OutputBaseFilename=AutoFM_Setup_v1.0.0

[Files]
Source: "dist\원가산정.exe"; DestDir: "{app}"
Source: "data\*"; DestDir: "{app}\data"; Flags: recursesubdirs

[Icons]
Name: "{group}\원가산정"; Filename: "{app}\원가산정.exe"
Name: "{commondesktop}\원가산정"; Filename: "{app}\원가산정.exe"
```

---

## 4. 업데이트 배포 / Deploy Updates

### 버전 관리
```python
# src/version.py
__version__ = "1.0.0"
__build_date__ = "2026-02-14"
```

### 변경사항 문서화
```markdown
# CHANGELOG.md

## [1.0.0] - 2026-02-14

### Added
- 사용자 매뉴얼 추가
- 설치 가이드 추가

### Changed
- InputPanel에서 보험요율 입력 제거

### Fixed
- ComboBox 드롭다운 미표시 문제 수정
```

---

## 5. 롤백 절차 / Rollback Procedure

문제 발생 시 이전 버전으로 복구:

1. 이전 버전 EXE 파일 확인
2. 사용자 데이터 백업 (`scenarios/` 폴더)
3. 이전 버전 재배포
4. 사용자에게 공지
5. 문제 원인 분석 및 수정
```

---

## 📸 Screenshot Specifications

### Screenshot Requirements

| ID | Screen | Description | Size | Format |
|----|--------|-------------|------|--------|
| SS-01 | Main Window | Full app window | 1920x1080 | PNG |
| SS-02 | Base Year Tab | Base year selection | 1200x800 | PNG |
| SS-03 | Job Role Table | With sample data | 1200x600 | PNG |
| SS-04 | Expense Input | Fixed expenses | 1200x600 | PNG |
| SS-05 | Expense Input | Variable expenses | 1200x600 | PNG |
| SS-06 | Summary Panel | Calculation results | 1000x600 | PNG |
| SS-07 | Labor Detail | Detailed breakdown | 1200x800 | PNG |
| SS-08 | Expense Detail | Expense breakdown | 1200x800 | PNG |
| SS-09 | Compare Page | Scenario comparison | 1200x800 | PNG |
| SS-10 | Settings Dialog | Insurance rates setting | 800x600 | PNG |
| SS-11 | Save Dialog | Scenario save dialog | 800x500 | PNG |
| SS-12 | Export PDF | PDF export preview | 900x700 | PNG |
| SS-13 | Export Excel | Excel file opened | 1200x800 | PNG |
| SS-14 | Donut Chart | Cost breakdown chart | 600x600 | PNG |
| SS-15 | Error Example | Common error message | 800x400 | PNG |

### Screenshot Guidelines
1. **Use Korean UI**: All screenshots must show Korean interface
2. **Sample Data**: Use realistic but non-sensitive example data
3. **Annotations**: Add arrows/labels where needed
4. **Consistent Style**: Same window size and theme
5. **High Quality**: 300 DPI for print, 96 DPI for web

### Screenshot Directory Structure
```
docs/
  screenshots/
    00-overview/
      main-window.png
      menu-bar.png
    01-base-year/
      base-year-tab.png
    02-job-input/
      job-table-empty.png
      job-table-filled.png
      job-combo box.png
    03-expense-input/
      expense-fixed.png
      expense-variable.png
      expense-passthrough.png
    04-calculation/
      summary-before.png
      summary-after.png
      donut-chart.png
    05-details/
      labor-detail.png
      expense-detail.png
    06-comparison/
      compare-page.png
      compare-table.png
    07-export/
      pdf-dialog.png
      excel-file.png
    08-errors/
      error-no-data.png
      error-validation.png
```

---

## 💾 Example Data Specifications

### Example Scenario 1: 건물 관리 (Building Management)
```json
{
  "scenario_name": "A동 건물관리 2024",
  "base_year": 2024,
  "monthly_workdays": 20.6,
  "daily_work_hours": 8.0,
  "job_inputs": {
    "FM_MANAGER": {
      "headcount": 1,
      "work_days": 20.6,
      "work_hours": 8.0,
      "overtime_hours": 0.0,
      "holiday_hours": 0.0
    },
    "FACILITY_TECH": {
      "headcount": 2,
      "work_days": 20.6,
      "work_hours": 8.0,
      "overtime_hours": 1.0,
      "holiday_hours": 0.5
    },
    "SECURITY_GUARD": {
      "headcount": 3,
      "work_days": 20.6,
      "work_hours": 8.0,
      "overtime_hours": 0.0,
      "holiday_hours": 0.0
    },
    "CLEANER": {
      "headcount": 2,
      "work_days": 20.6,
      "work_hours": 4.0,
      "overtime_hours": 0.0,
      "holiday_hours": 0.0
    }
  },
  "expense_inputs": [
    {"exp_code": "FIX_INS_INDUST", "unit_price": 0, "quantity": 1},
    {"exp_code": "FIX_INS_PENSION", "unit_price": 0, "quantity": 1},
    {"exp_code": "VAR_CLOTH", "unit_price": 50000, "quantity": 8},
    {"exp_code": "VAR_WELFARE", "unit_price": 30000, "quantity": 8}
  ]
}
```

### Example Scenario 2: 소규모 시설 (Small Facility)
```json
{
  "scenario_name": "B동 소규모 2025",
  "base_year": 2025,
  "monthly_workdays": 22.0,
  "daily_work_hours": 8.0,
  "job_inputs": {
    "FACILITY_TECH": {
      "headcount": 1,
      "work_days": 22.0,
      "work_hours": 8.0,
      "overtime_hours": 0.0,
      "holiday_hours": 0.0
    },
    "CLEANER": {
      "headcount": 1,
      "work_days": 22.0,
      "work_hours": 4.0,
      "overtime_hours": 0.0,
      "holiday_hours": 0.0
    }
  }
}
```

---

## 🔄 Implementation Order

### Phase 1: Error Verification (Complete ✅)
- [x] Run app and collect logs
- [x] Verify no import errors
- [x] Verify no PyQt6 errors
- [x] Verify database connection
- [x] Verify all tabs load

### Phase 2: Screenshot Preparation (Next)
1. Prepare sample data scenarios
2. Run app with sample data
3. Capture all 15 screenshots
4. Annotate screenshots with labels
5. Organize in `docs/screenshots/` directory

### Phase 3: USER_GUIDE.md Creation
1. Create document structure
2. Write Section 1 (시작하기)
3. Write Section 2 (기본 개념)
4. Write Sections 3-8 (핵심 기능)
5. Write Section 9 (고급 기능)
6. Write Section 10 (문제 해결)
7. Write Section 11 (부록)
8. Insert all screenshots
9. Review and proofread

### Phase 4: INSTALL.md Creation
1. Write system requirements
2. Write Python setup instructions
3. Write dependency installation
4. Write database initialization
5. Write first run guide
6. Write troubleshooting

### Phase 5: DEPLOY.md Creation
1. Document EXE build process
2. Create build scripts
3. Write deployment checklist
4. Document installer creation
5. Write update deployment guide
6. Write rollback procedure

### Phase 6: Testing & Review
1. Test all instructions in USER_GUIDE.md
2. Verify all screenshots are correct
3. Test installation on clean PC
4. Test build scripts
5. Final proofreading
6. Version control commit

---

## 📊 Quality Metrics

### Documentation Quality

| Metric | Target | Measurement |
|--------|--------|-------------|
| Completeness | 100% | All sections written |
| Screenshots | 15+ | All required screens captured |
| Readability | High | Flesch Reading Ease > 60 |
| Accuracy | 100% | All steps tested and verified |
| Language | Korean | Primary language for users |
| Technical Depth | Appropriate | Match user expertise level |

### Code Quality
| Metric | Target | Status |
|--------|--------|--------|
| Error Rate | 0% | ✅ Complete |
| Warning Rate | < 5% | ✅ Acceptable |
| Feature Coverage | 100% | ⏳ In Progress |

---

## 🔗 Dependencies & References

### Internal Documents
- [Plan Document](../../01-plan/features/app-stability-and-user-manual.plan.md)
- [Main Window Implementation](../../src/ui/main_window.py)
- [Database Schema](../../src/domain/db.py)

### External Resources
- PyQt6 Documentation: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- Markdown Guide: https://www.markdownguide.org/
- Technical Writing Best Practices: https://developers.google.com/tech-writing

---

## 📝 Notes

### Writing Guidelines
1. **User-Centric**: Write from user's perspective
2. **Clear Language**: Avoid jargon, use simple Korean
3. **Visual Aids**: Screenshot for every complex step
4. **Examples**: Provide realistic examples
5. **Troubleshooting**: Anticipate common problems

### Maintenance
- **Review Frequency**: Every major release
- **Update Trigger**: When UI changes occur
- **Version Control**: Track changes in git
- **Feedback Loop**: Collect user feedback

---

## ✅ Acceptance Criteria

- [ ] USER_GUIDE.md created (3000+ lines)
- [ ] 15+ screenshots captured and annotated
- [ ] INSTALL.md created (500+ lines)
- [ ] DEPLOY.md created (600+ lines)
- [ ] All example scenarios tested
- [ ] All instructions verified on clean PC
- [ ] Build scripts tested and working
- [ ] Korean language quality reviewed
- [ ] Technical accuracy verified
- [ ] User feedback collected and incorporated

---

**Design approved by**: Development Team
**Review date**: 2026-02-14
**Ready for implementation**: ✅ Yes
**Next step**: `/pdca do app-stability-and-user-manual`

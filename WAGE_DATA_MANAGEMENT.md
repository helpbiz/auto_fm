# 연도별 노임단가 관리 가이드

Auto FM에서 연도별 노임단가를 JSON 파일로 관리하고 데이터베이스로 임포트하는 방법을 설명합니다.

---

## 📋 개요

### 기능
- **연도별 노임단가** JSON 파일 관리
- **직무코드-등급 매핑** 관리
- **자동 임포트** 도구 제공
- **데이터베이스 통합** (기존 Auto FM과 호환)

### 장점
- ✅ Excel 대신 JSON으로 관리 (Git 버전 관리 가능)
- ✅ 연도별 데이터 독립 관리
- ✅ 직무코드 표준화
- ✅ 자동 계산 (시간급 = 일급 ÷ 8)

---

## 📁 파일 구조

```
auto_fm/
├── data/
│   ├── wages_master.json        # 연도별 노임단가
│   └── job_mapping.json         # 직무코드 매핑
├── src/
│   └── utils/
│       └── json_importer.py     # 임포트 유틸리티
└── import_wages.py               # CLI 임포트 도구
```

---

## 1️⃣ 데이터 파일 편집

### data/wages_master.json

연도별, 등급별 노임단가 정의:

```json
{
  "2025": {
    "고급기술자": 318000,
    "중급기술자": 269000,
    "초급기술자": 234000,
    "특급기술자": 380000,
    "단순노무종사원": 93000
  },
  "2026": {
    "고급기술자": 330000,
    "중급기술자": 280000,
    ...
  }
}
```

**등급 추가 방법**:
```json
"2025": {
  "고급기술자": 318000,
  "신규등급": 250000     // ← 새 등급 추가
}
```

### data/job_mapping.json

직무코드와 등급/부서 매핑:

```json
{
  "M101": {
    "title": "소장",
    "grade": "고급기술자",
    "dept": "관리팀",
    "description": "시설 총괄 관리"
  },
  "M201": {
    "title": "과장",
    "grade": "중급기술자",
    "dept": "관리팀",
    "description": "현장 관리 감독"
  }
}
```

**직무 추가 방법**:
```json
{
  "M101": { ... },
  "M401": {                      // ← 새 직무 추가
    "title": "부장",
    "grade": "특급기술자",
    "dept": "관리팀",
    "description": "현장 총괄"
  }
}
```

---

## 2️⃣ 데이터 임포트

### CLI 도구 사용

```bash
# 2025년 데이터 임포트
python import_wages.py 2025

# 2024년 데이터 임포트
python import_wages.py 2024
```

### 출력 예시

```
============================================================
  연도별 노임단가 임포트 도구
============================================================

[대상 연도] 2025
[데이터 소스] data/wages_master.json, data/job_mapping.json

============================================================
  [OK] 임포트 완료!
============================================================
  시나리오 ID: year_2025
  등록된 직무: 6개

[참고] Auto FM에서 시나리오 'year_2025'로 불러와서 사용하세요.
```

---

## 3️⃣ Auto FM에서 사용

### 방법 1: GUI에서 시나리오 로드

1. Auto FM 실행
2. 파일 → 시나리오 불러오기
3. **"year_2025"** 시나리오 선택
4. 노무비 입력 시 자동으로 단가 적용됨

### 방법 2: 코드에서 직접 사용

```python
from domain.db import get_connection
from domain.masterdata.repo import MasterDataRepo

conn = get_connection()
repo = MasterDataRepo(conn)

# 2025년 노임단가 조회
scenario_id = "year_2025"
job_roles = repo.get_job_roles(scenario_id)

for job in job_roles:
    print(f"{job['job_code']}: {job['job_name']}")
```

---

## 4️⃣ 데이터 검증

### 임포트된 데이터 확인

```python
python << 'EOF'
import sqlite3
from pathlib import Path
import os

db_path = Path(os.getenv('LOCALAPPDATA')) / 'auto_fm' / 'app.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    SELECT 
        jr.job_code,
        jr.job_name,
        jrate.wage_day,
        jrate.wage_hour
    FROM md_job_role jr
    JOIN md_job_rate jrate ON jr.scenario_id = jrate.scenario_id 
                           AND jr.job_code = jrate.job_code
    WHERE jr.scenario_id = 'year_2025'
    ORDER BY jr.sort_order
""")

for row in cursor.fetchall():
    print(f"{row[0]:<10} {row[1]:<15} {row[2]:>12,}원 {row[3]:>10,}원")

conn.close()

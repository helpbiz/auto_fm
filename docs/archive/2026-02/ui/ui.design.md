# UI 기능 설계 문서 (auto_fm)

> **Feature**: UI 개선 및 자동 계산 기능
> **Created**: 2026-02-14
> **Status**: Design
> **Author**: PDCA System

---

## 1. 개요 (Overview)

### 1.1 목적
auto_fm (시설관리 원가 계산 프로그램)의 UI 컴포넌트를 개선하고, 자동 계산 기능을 추가하여 사용자 편의성을 향상시킵니다.

### 1.2 범위
- 직무별 인원 입력 테이블 개선
- 경비 항목 입력 테이블 개선
- 노무비/경비 상세 테이블에 합계 행 추가
- 인적 보험료 자동 계산
- 시나리오 데이터 보존 로직
- 인원수 기반 경비 계산

---

## 2. 요구사항 (Requirements)

### 2.1 기능 요구사항 (Functional Requirements)

#### FR-1: 노무비 상세 테이블 합계 행 표시
- **요구사항**: 노무비 상세 테이블 하단에 각 컬럼의 합계 행을 표시
- **입력**: 직무별 노무비 계산 결과 리스트
- **출력**: 인원, 기본급, 제수당, 보험료, 인건비 소계, 산정 금액의 합계 행
- **스타일**: 굵은 글씨, 회색 배경 (RGB 240, 240, 240)

#### FR-2: 경비 상세 테이블 월계/연간합계 분리
- **요구사항**: 경비 상세 테이블에 월계와 연간합계를 별도 컬럼으로 표시
- **입력**: 경비 항목별 월 단위 금액 (row_total)
- **출력**:
  - 월계: row_total (천 단위 콤마)
  - 연간합계: row_total × 12 (천 단위 콤마)
- **컬럼 구성**: 구분, 항목명, 월계, 연간합계, 유형

#### FR-3: 경비 상세 테이블 합계 행 표시
- **요구사항**: 경비 상세 테이블 하단에 월계/연간합계의 합계 행 표시
- **스타일**: 굵은 글씨, 회색 배경 (RGB 240, 240, 240)

#### FR-4: 인적 보험료 자동 계산
- **요구사항**: 직무별 인원 입력 시 7가지 인적 보험료를 자동으로 계산하여 경비 입력 테이블에 반영
- **트리거**: 직무별 인원 테이블의 인원 수 변경 시
- **계산 대상 항목**:
  1. 산재보험료 (FIX_INS_INDUST)
  2. 국민연금 (FIX_INS_PENSION)
  3. 고용보험료 (FIX_INS_EMPLOY)
  4. 국민건강보험료 (FIX_INS_HEALTH)
  5. 노인장기요양보험료 (FIX_INS_LONGTERM)
  6. 임금채권보장보험료 (FIX_INS_WAGE)
  7. 석면피해구제분담금 (FIX_INS_ASBESTOS)
- **계산 로직**:
  - 직무별 인원 → 노무비 계산 → 보험료 산출
  - 경비 입력 테이블의 해당 항목 자동 업데이트

#### FR-5: 시나리오 불러오기 시 데이터 보존
- **문제**: 시나리오 불러오기 시 마스터 데이터 새로고침으로 인해 현재 입력된 직무별 인원 데이터가 초기화됨
- **해결책**:
  1. 마스터 데이터 새로고침 전에 현재 입력값 임시 저장
  2. 불러온 시나리오에 저장된 데이터가 있으면 해당 데이터 적용
  3. 불러온 시나리오에 저장된 데이터가 없으면 임시 저장한 현재 입력값 복원
- **영향 범위**: `main_window.py::load_scenario()` 메서드

#### FR-6: 인원수 기반 경비 항목 계산
- **요구사항**: 특정 경비 항목의 연간합계는 직무별 인원 합계를 곱하여 계산
- **대상 항목**:
  - 피복비 (FIX_WEL_CLOTH)
  - 식대 (FIX_WEL_MEAL)
  - 건강검진비 (FIX_WEL_CHECKUP)
  - 의약품비 (FIX_WEL_MEDICINE)
- **계산 로직**:
  - **대상 항목**: `연간합계 = 월계 × 인원합계 × 12`
  - **기타 항목**: `연간합계 = 월계 × 12`
- **인원합계 계산**: `sum(직무별 인원 테이블의 모든 headcount)`

#### FR-7: 경비 입력 테이블에 경비코드 컬럼 표시
- **요구사항**: 경비 세부 항목 테이블의 각 행에 경비코드(exp_code)를 표시하여 가독성 향상
- **현재 문제**:
  - 콤보박스로 경비코드 선택 시 해당 경비코드의 세부 항목만 테이블에 표시
  - 테이블의 각 행이 어떤 경비코드에 속하는지 테이블만 봐서는 알 수 없음
  - 경비코드 확인을 위해 위쪽 콤보박스를 확인해야 함
- **해결 방안**:
  - 콤보박스 방식 유지 (세부 항목 관리 용이)
  - 테이블에 "경비코드" 컬럼 추가 (첫 번째 컬럼)
  - 경비코드 컬럼은 읽기 전용 (현재 선택된 경비코드로 자동 설정)
- **컬럼 구성** (기존 9개 → 10개):
  - **경비코드** (새로 추가, 읽기 전용)
  - 세부코드
  - 항목명
  - 규격
  - 단위
  - 수량
  - 단가
  - 금액
  - 비고
  - 정렬
- **영향 범위**: `src/ui/expense_sub_item_table.py`

### 2.2 비기능 요구사항 (Non-Functional Requirements)

#### NFR-1: 성능
- 인원 수 변경 시 보험료 자동 계산은 500ms 이내 완료
- 테이블 갱신 시 화면 깜빡임 최소화 (signal blocking 활용)

#### NFR-2: 사용성
- 천 단위 콤마 구분으로 금액 가독성 향상
- 합계 행은 시각적으로 구분 (굵은 글씨 + 회색 배경)
- Pass-through 항목은 빨간색으로 강조 (RGB 198, 40, 40)

#### NFR-3: 데이터 무결성
- 시나리오 불러오기 시 사용자 입력 데이터 보존
- 계산 로직 변경 시 기존 저장된 시나리오와 호환성 유지

---

## 3. 아키텍처 설계 (Architecture Design)

### 3.1 컴포넌트 구조

```
MainWindow (src/ui/main_window.py)
├── InputPanel (좌측)
│   ├── JobRoleTable (직무별 인원 입력)
│   │   └─[signal] table.itemChanged → _on_job_role_changed()
│   └── ExpenseInputTable (경비 항목 입력)
│
├── SummaryPanel (우측 상단)
│   └── DonutChart
│
├── LaborDetailTable (우측 중단)
│   └─[new] update_rows() - 합계 행 추가
│
└── ExpenseDetailTable (우측 하단)
    └─[new] update_rows(rows, total_headcount) - 월계/연간합계 분리 + 합계 행
```

### 3.2 데이터 흐름

```
[사용자 입력]
    ↓
JobRoleTable.itemChanged
    ↓
MainWindow._on_job_role_changed()
    ├─→ calculate() 호출
    │   ├─→ LaborCalculator 실행
    │   ├─→ ExpenseCalculator 실행
    │   └─→ Aggregator 생성
    │
    ├─→ LaborDetailTable.update_rows(labor_rows)
    │   └─→ [합계 행 계산 및 추가]
    │
    ├─→ ExpenseDetailTable.update_rows(expense_rows, total_headcount)
    │   ├─→ [인원수 기반 연간합계 계산]
    │   └─→ [합계 행 계산 및 추가]
    │
    └─→ ExpenseInputTable 보험료 자동 업데이트
        └─→ [7가지 보험료 항목 갱신]
```

### 3.3 시나리오 로드 흐름

```
[시나리오 선택]
    ↓
MainWindow.load_scenario(scenario_id)
    ├─→ [1] current_job_inputs = get_job_inputs() (현재 입력값 저장)
    ├─→ [2] canonical = get_scenario_input(scenario_id) (DB에서 로드)
    ├─→ [3] _refresh_master_data(scenario_id) (마스터 데이터 새로고침)
    └─→ [4] if canonical.labor.job_roles:
            _apply_canonical_input(canonical) (저장된 데이터 적용)
        else:
            set_job_inputs(current_job_inputs) (현재 입력값 복원)
```

---

## 4. UI 컴포넌트 설계

### 4.1 LaborDetailTable (노무비 상세 테이블)

#### 컬럼 구성
| 컬럼 | 데이터 타입 | 설명 |
|------|-------------|------|
| 직무/직책 | str | 직무명 |
| 인원 | int | 인원 수 |
| 기본급 | int (천 단위 콤마) | 월 기본급 |
| 제수당 | int (천 단위 콤마) | 월 제수당 |
| 보험료 | int (천 단위 콤마) | 월 보험료 |
| 인건비 소계 | int (천 단위 콤마) | 월 인건비 소계 |
| 산정 금액 | int (천 단위 콤마) | 월 총 금액 |

#### 합계 행 스타일
```python
font: Bold
background: QColor(240, 240, 240)
text: "합계"
```

#### 구현 메서드
```python
def update_rows(self, rows: list[dict]) -> None:
    """
    노무비 상세 행 업데이트 + 합계 행 추가

    Args:
        rows: [
            {
                "role": str,
                "headcount": int,
                "base_salary": int,
                "allowances": int,
                "insurance_total": int,
                "labor_subtotal": int,
                "role_total": int
            },
            ...
        ]
    """
    # 1. 기존 행 제거
    # 2. 데이터 행 추가
    # 3. 합계 계산
    # 4. 합계 행 추가 (굵은 글씨 + 회색 배경)
```

### 4.2 ExpenseDetailTable (경비 상세 테이블)

#### 컬럼 구성
| 컬럼 | 데이터 타입 | 설명 |
|------|-------------|------|
| 구분 | str | FIXED/VARIABLE/PASSTHROUGH |
| 항목명 | str | 경비 항목명 |
| 월계 | int (천 단위 콤마) | 월 단위 금액 |
| 연간합계 | int (천 단위 콤마) | 연간 총 금액 |
| 유형 | str | 경비 유형 |

#### 연간합계 계산 로직
```python
PER_PERSON_ITEMS = {"피복비", "식대", "건강검진비", "의약품비"}

if expense_name in PER_PERSON_ITEMS:
    annual_total = row_total * total_headcount * 12
else:
    annual_total = row_total * 12
```

#### 합계 행 스타일
- Pass-through 항목: 빨간색 (RGB 198, 40, 40)
- 합계 행: 굵은 글씨 + 회색 배경

#### 구현 메서드
```python
def update_rows(self, rows: list[dict], total_headcount: int = 1) -> None:
    """
    경비 상세 행 업데이트 + 월계/연간합계 분리 + 합계 행 추가

    Args:
        rows: [
            {
                "category": str,
                "name": str,
                "row_total": int,  # 월 단위 금액
                "type": str
            },
            ...
        ]
        total_headcount: 직무별 인원 합계 (기본값: 1)
    """
    # 1. 기존 행 제거
    # 2. 데이터 행 추가
    #    - 월계 = row_total
    #    - 연간합계 = row_total × (total_headcount if PER_PERSON else 1) × 12
    # 3. 합계 계산
    # 4. 합계 행 추가
```

### 4.3 MainWindow 이벤트 핸들러

#### _on_job_role_changed (인원 변경 이벤트)
```python
def _on_job_role_changed(self, item: QTableWidgetItem) -> None:
    """
    직무별 인원 변경 시 자동 계산 및 보험료 업데이트

    Workflow:
    1. 현재 입력값 수집
    2. calculate() 호출하여 노무비/경비 계산
    3. 결과를 상세 테이블에 반영
    4. 인적 보험료 7개 항목을 경비 입력 테이블에 자동 업데이트
    """
```

#### load_scenario (시나리오 로드)
```python
def load_scenario(self, scenario_id: str) -> None:
    """
    시나리오 불러오기 + 데이터 보존

    Workflow:
    1. 현재 직무별 인원 입력값 임시 저장
    2. DB에서 시나리오 데이터 로드
    3. 마스터 데이터 새로고침 (테이블 초기화)
    4. if 저장된 데이터 존재:
           저장된 데이터 적용
       else:
           임시 저장한 현재 입력값 복원
    """
```

---

## 5. 데이터 모델

### 5.1 Labor Detail Row
```python
{
    "role": str,              # 직무명
    "headcount": int,         # 인원 수
    "base_salary": int,       # 월 기본급
    "allowances": int,        # 월 제수당
    "insurance_total": int,   # 월 보험료
    "labor_subtotal": int,    # 월 인건비 소계
    "role_total": int         # 월 총 금액
}
```

### 5.2 Expense Detail Row
```python
{
    "category": str,      # 구분 (FIXED/VARIABLE/PASSTHROUGH)
    "name": str,          # 항목명
    "row_total": int,     # 월 단위 금액
    "type": str           # 유형
}
```

### 5.3 인적 보험료 항목 코드
```python
INSURANCE_EXPENSE_CODES = [
    "FIX_INS_INDUST",     # 산재보험료
    "FIX_INS_PENSION",    # 국민연금
    "FIX_INS_EMPLOY",     # 고용보험료
    "FIX_INS_HEALTH",     # 국민건강보험료
    "FIX_INS_LONGTERM",   # 노인장기요양보험료
    "FIX_INS_WAGE",       # 임금채권보장보험료
    "FIX_INS_ASBESTOS"    # 석면피해구제분담금
]
```

### 5.4 인원수 기반 경비 항목
```python
PER_PERSON_EXPENSE_NAMES = {
    "피복비",      # FIX_WEL_CLOTH
    "식대",        # FIX_WEL_MEAL
    "건강검진비",  # FIX_WEL_CHECKUP
    "의약품비"     # FIX_WEL_MEDICINE
}
```

---

## 6. 구현 체크리스트

### 6.1 Phase 1: 테이블 합계 행 추가 ✅
- [x] LaborDetailTable.update_rows() - 합계 행 추가
- [x] ExpenseDetailTable - 월계/연간합계 컬럼 분리
- [x] ExpenseDetailTable.update_rows() - 합계 행 추가
- [x] 합계 행 스타일 적용 (굵은 글씨 + 회색 배경)

### 6.2 Phase 2: 인적 보험료 자동 계산 ✅
- [x] MainWindow._on_job_role_changed() 구현
- [x] JobRoleTable.itemChanged 시그널 연결
- [x] 7가지 보험료 자동 계산 로직
- [x] ExpenseInputTable 자동 업데이트

### 6.3 Phase 3: 시나리오 데이터 보존 ✅
- [x] MainWindow.load_scenario() - 현재 입력값 임시 저장
- [x] 마스터 데이터 새로고침 전후 데이터 처리
- [x] signal blocking으로 불필요한 이벤트 방지

### 6.4 Phase 4: 인원수 기반 경비 계산 ✅
- [x] ExpenseDetailTable.update_rows() - total_headcount 매개변수 추가
- [x] PER_PERSON_ITEMS 집합 정의
- [x] 조건부 연간합계 계산 로직
- [x] MainWindow의 모든 update_rows() 호출 지점 업데이트 (6개소)
  - [x] Line 274: _open_scenario_manager (clear)
  - [x] Line 303: _on_tab_changed (tab switch)
  - [x] Line 346: calculate (실행 버튼)
  - [x] Line 577: load_scenario (snapshot 성공)
  - [x] Line 597: load_scenario (snapshot 실패)
  - [x] Line 655: delete_scenario (삭제 후 초기화)

### 6.5 Phase 5: 테스트 및 검증 (예정)
- [ ] 인원 수 변경 시 보험료 자동 계산 확인
- [ ] 시나리오 저장/불러오기 테스트
- [ ] 인원수 기반 경비 계산 검증
- [ ] 합계 행 계산 정확도 검증
- [ ] 천 단위 콤마 표시 확인

### 6.6 Phase 6: 경비 입력 테이블 경비코드 컬럼 추가 (진행 중)
- [ ] ExpenseSubItemTable 컬럼 수 9개 → 10개로 변경
- [ ] 컬럼 인덱스 상수 업데이트 (COL_EXP_CODE = 0, 나머지 +1)
- [ ] _default_headers에 "경비코드" 추가
- [ ] _set_row() - 경비코드 컬럼에 self._current_exp_code 설정 (읽기 전용)
- [ ] _get_row() - 경비코드 컬럼 읽기 (검증용)
- [ ] 경비코드 컬럼 ItemFlags 설정 (읽기 전용)

---

## 7. 파일 목록

### 7.1 수정된 파일
- `src/ui/labor_detail_table.py` - 합계 행 추가
- `src/ui/expense_detail_table.py` - 월계/연간합계 분리 + 합계 행 + 인원수 기반 계산
- `src/ui/main_window.py` - 자동 계산 + 시나리오 데이터 보존 + total_headcount 전달

### 7.2 관련 파일
- `src/domain/calculator/labor.py` - 노무비 계산 로직
- `src/domain/calculator/expense.py` - 경비 계산 로직
- `src/domain/masterdata/seeds/20260214_seed_expense_items.sql` - 경비 항목 시드 데이터
- `src/domain/scenario_input/service.py` - 시나리오 저장/로드

---

## 8. 제약사항 및 주의사항

### 8.1 제약사항
- PyQt6 QTableWidget 사용 (PyQt5 호환성 유지 불필요)
- SQLite 데이터베이스 사용
- 기존 저장된 시나리오와 호환성 유지

### 8.2 주의사항
- signal blocking 필수: 테이블 데이터 직접 수정 시 무한 루프 방지
- total_headcount 계산: 0일 경우에도 에러 없이 처리 (기본값 1 또는 0)
- Pass-through 항목: 빨간색 표시로 사용자에게 특별히 주의 표시

---

## 9. 향후 개선 사항

### 9.1 성능 최적화
- 대량 데이터 처리 시 테이블 갱신 최적화
- 계산 로직 캐싱

### 9.2 사용성 개선
- 합계 행 고정 (스크롤 시 항상 표시)
- 컬럼 너비 자동 조정
- 툴팁으로 계산식 표시

### 9.3 기능 확장
- 경비 항목별 계산식 사용자 정의
- 엑셀 내보내기 시 합계 행 포함
- 비교 페이지에도 합계 행 표시

---

## 10. 참고 문서

- [Excel auto_fm_fin.xlsx 경비집계표](src/auto_fm_fin.xlsx)
- [표17-40 인적보험료 및 복리후생비](data/wages_master.json)
- [PDCA Status](.pdca-status.json)

---

**End of Design Document**

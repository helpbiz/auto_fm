# auto_fm 시설관리 원가 계산 프로그램 - 설계 문서

> **Feature**: auto_fm 전체 프로그램
> **Plan Reference**: [auto_fm.plan.md](../../01-plan/features/auto_fm.plan.md)
> **Created**: 2026-02-14
> **Updated**: 2026-02-14 (실제 구현 반영)
> **Status**: Design (Implementation-Aligned)
> **Author**: PDCA System

**⚠️ 중요**: 이 설계 문서는 **실제 구현된 아키텍처를 반영**하여 업데이트되었습니다.
- **데이터베이스**: 시나리오별 마스터 데이터 + JSON 저장 방식
- **계산 로직**: 상여금, 주휴수당, 연차수당, 퇴직금 포함한 확장 모델
- **UI 구조**: 좌측 입력 | 중앙 7개 탭 | 우측 차트
- **일반관리비/이윤**: 실제 구현에서 입력 및 계산 기능 포함

---

## 1. 아키텍처 개요 (Architecture Overview)

### 1.1 시스템 구조

```
┌─────────────────────────────────────────────────────────────┐
│                        UI Layer (PyQt6)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Input Panel  │  │ Detail Tables│  │ Summary Panel│      │
│  │ - 기본정보    │  │ - 노무비상세  │  │ - 집계       │      │
│  │ - 직무인원    │  │ - 경비상세    │  │ - 차트       │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │               │
│         └──────────────────┴──────────────────┘               │
│                            │                                  │
├────────────────────────────┼──────────────────────────────────┤
│                    Service Layer                              │
│  ┌─────────────────────────┴──────────────────────────────┐  │
│  │  Calculator          │  MasterData     │  Scenario      │  │
│  │  - Labor Calculator  │  - Job Roles    │  - Save/Load   │  │
│  │  - Expense Calculator│  - Wages        │  - Compare     │  │
│  │  - Insurance         │  - Expense Items│  - Export      │  │
│  └─────────────────────────┬──────────────────────────────┘  │
│                            │                                  │
├────────────────────────────┼──────────────────────────────────┤
│                    Data Layer (SQLite)                        │
│  ┌─────────────────────────┴──────────────────────────────┐  │
│  │  md_job_roles  │  md_wages  │  scenarios  │  results   │  │
│  │  md_expense_items  │  expense_sub_items  │  migrations │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 레이어별 책임

| Layer | 책임 | 주요 컴포넌트 |
|-------|------|--------------|
| UI Layer | 사용자 입력, 결과 표시, 이벤트 처리 | main_window, input_panel, tables |
| Service Layer | 비즈니스 로직, 계산, 데이터 변환 | calculator/, masterdata/, result/ |
| Data Layer | 데이터 영속화, 마이그레이션 | db.py, migration_runner.py |

---

## 2. 데이터베이스 설계 (Database Schema)

### 2.1 아키텍처 개요

**실제 구현 아키텍처**: **시나리오별 마스터 데이터 + JSON 저장 방식**

이 아키텍처는 다음과 같은 장점을 제공합니다:
- 시나리오별 독립적인 직무코드 및 임금 관리
- 유연한 데이터 구조 (JSON 스키마)
- 빠른 조회 성능 (적은 JOIN)
- 시나리오 삭제 시 관련 데이터 자동 정리 (CASCADE)

### 2.2 테이블 정의

#### 2.2.1 md_job_role (직무 마스터 - 시나리오별)
```sql
CREATE TABLE md_job_role (
    scenario_id TEXT NOT NULL,       -- 시나리오 ID
    job_code TEXT NOT NULL,          -- 직무코드 (예: MGR01)
    job_name TEXT NOT NULL,          -- 직무명 (예: 관리감독자)
    sort_order INTEGER NOT NULL DEFAULT 0,  -- 정렬 순서
    is_active INTEGER NOT NULL DEFAULT 1,   -- 활성 상태
    PRIMARY KEY (scenario_id, job_code)
);
```

**특징**:
- 시나리오별로 독립적인 직무 관리
- Composite Primary Key: (scenario_id, job_code)
- 각 시나리오마다 다른 직무 구성 가능

#### 2.2.2 md_job_rate (임금 마스터 - 시나리오별)
```sql
CREATE TABLE md_job_rate (
    scenario_id TEXT NOT NULL,       -- 시나리오 ID
    job_code TEXT NOT NULL,          -- 직무코드
    wage_day INTEGER NOT NULL,       -- 일일 임금
    wage_hour INTEGER NOT NULL,      -- 시간당 임금
    allowance_rate_json TEXT NOT NULL,  -- 수당률 JSON
    PRIMARY KEY (scenario_id, job_code),
    FOREIGN KEY (scenario_id, job_code)
        REFERENCES md_job_role(scenario_id, job_code) ON DELETE CASCADE
);
```

**allowance_rate_json 구조**:
```json
{
    "bonus_rate": 4.0,           // 상여금율 (400% / 12개월)
    "weekly_holiday_days": 4.33, // 주휴일수
    "annual_leave_days": 1.25,   // 연차일수
    "overtime_rate": 1.5,        // 연장근로 가산율
    "holiday_work_rate": 2.0     // 휴일근로 가산율
}
```

#### 2.2.3 md_expense_item (경비 항목 마스터 - 시나리오별)
```sql
CREATE TABLE md_expense_item (
    scenario_id TEXT NOT NULL,       -- 시나리오 ID
    exp_code TEXT NOT NULL,          -- 경비코드 (예: FIX_INS_INDUST)
    exp_name TEXT NOT NULL,          -- 경비명 (예: 산재보험료)
    group_code TEXT NOT NULL,        -- 그룹 (FIXED, VARIABLE, AGENCY)
    sort_order INTEGER NOT NULL DEFAULT 0,  -- 정렬 순서
    is_active INTEGER NOT NULL DEFAULT 1,   -- 활성 상태
    PRIMARY KEY (scenario_id, exp_code)
);
```

**그룹 코드**:
- `FIXED`: 고정비 (보험료, 임대료 등)
- `VARIABLE`: 변동비 (피복비, 식대, 의약품비 등)
- `PASSTHROUGH`: 대행비 (폐기물처리, 승강기보험 등)

#### 2.2.4 md_expense_pricebook (경비 단가 - 시나리오별)
```sql
CREATE TABLE md_expense_pricebook (
    scenario_id TEXT NOT NULL,       -- 시나리오 ID
    exp_code TEXT NOT NULL,          -- 경비코드
    unit_price INTEGER NOT NULL,     -- 단가
    unit TEXT NOT NULL,              -- 단위
    effective_from TEXT NOT NULL,    -- 적용 시작일
    effective_to TEXT,               -- 적용 종료일
    PRIMARY KEY (scenario_id, exp_code, effective_from),
    FOREIGN KEY (scenario_id, exp_code)
        REFERENCES md_expense_item(scenario_id, exp_code) ON DELETE CASCADE
);
```

#### 2.2.5 scenario_input (시나리오 입력 데이터 - JSON 저장)
```sql
CREATE TABLE scenario_input (
    scenario_id TEXT PRIMARY KEY,    -- 시나리오 ID
    input_json TEXT NOT NULL,        -- 입력 데이터 JSON
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

**input_json 구조**:
```json
{
    "metadata": {
        "scenario_name": "시나리오1",
        "overhead_rate": 18.5,
        "profit_rate": 15.0
    },
    "labor": {
        "job_roles": {
            "MGR01": {
                "headcount": 2,
                "work_days": 26,
                "work_hours": 8,
                "overtime_hours": 0,
                "holiday_work_hours": 0
            }
        }
    },
    "expenses": {
        "items": {
            "FIX_RENT": {
                "quantity": 1,
                "unit_price": 5000000
            }
        }
    }
}
```

#### 2.2.6 calculation_result (계산 결과 - JSON 저장)
```sql
CREATE TABLE calculation_result (
    scenario_id TEXT PRIMARY KEY,    -- 시나리오 ID
    result_json TEXT NOT NULL,       -- 계산 결과 JSON
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

**result_json 구조**:
```json
{
    "aggregator": {
        "labor_total": 10000000,
        "fixed_expense_total": 5000000,
        "variable_expense_total": 2000000,
        "passthrough_expense_total": 1000000,
        "overhead_cost": 2775000,
        "profit": 2666250,
        "grand_total": 23441250
    },
    "labor_rows": [...],
    "expense_rows": [...],
    "job_breakdown": [...],
    "insurance_by_exp_code": {...}
}
```

#### 2.2.7 expense_sub_item (경비 세부 항목 - 시나리오별)
```sql
CREATE TABLE expense_sub_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id TEXT NOT NULL,       -- 시나리오 ID
    exp_code TEXT NOT NULL,          -- 경비코드
    sub_code TEXT,                   -- 세부코드
    sub_name TEXT,                   -- 항목명
    spec TEXT,                       -- 규격
    unit TEXT,                       -- 단위
    quantity REAL,                   -- 수량
    unit_price INTEGER,              -- 단가
    amount INTEGER,                  -- 금액
    remark TEXT,                     -- 비고
    sort_order INTEGER DEFAULT 0,    -- 정렬 순서
    is_active INTEGER DEFAULT 1,     -- 활성 상태
    FOREIGN KEY (scenario_id, exp_code)
        REFERENCES md_expense_item(scenario_id, exp_code) ON DELETE CASCADE
);
```

#### 2.2.8 migrations (마이그레이션 이력)
```sql
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,
    applied_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 2.3 데이터 흐름

```
1. UI 입력 → scenario_input.input_json (JSON 저장)
2. 계산 실행 →
   - md_job_role, md_job_rate에서 직무/임금 조회
   - md_expense_item, expense_sub_item에서 경비 조회
   - 계산 로직 실행
3. 계산 결과 → calculation_result.result_json (JSON 저장)
4. UI 표시 → result_json 파싱하여 테이블에 표시
```

---

## 3. 계산 로직 설계 (Calculation Logic)

### 3.1 노무비 계산 (Labor Calculation)

#### 3.1.1 계산 흐름
```
1. 직무별 인원 입력 (scenario_input.input_json → labor.job_roles)
2. 직무 임금 조회 (md_job_rate → wage_day + allowance_rate_json)
3. 법정수당 계산 (상여금, 주휴수당, 연차수당, 연장근로, 휴일근로, 퇴직금)
4. 인적 보험료 계산 (7종)
5. 직무별 노무비 집계
6. 노무비 합계 산출
```

#### 3.1.2 노무비 계산식 (실제 구현)

```python
# 노무비 계산 흐름
def _calculate_labor(canonical: dict, job_roles: list, job_rates: dict) -> tuple:
    """
    Args:
        canonical: scenario_input.input_json 데이터
        job_roles: md_job_role 목록
        job_rates: {job_code: wage_day} 딕셔너리

    Returns:
        (labor_rows, labor_total, job_breakdown, insurance_aggregate)
    """

    labor_inputs = canonical.get("labor", {}).get("job_roles", {})

    for role in job_roles:
        if not role.is_active:
            continue

        values = labor_inputs.get(role.job_code)
        headcount = Decimal(str(values.get("headcount", 0)))
        work_days = Decimal(str(values.get("work_days", 0)))
        work_hours = Decimal(str(values.get("work_hours", 0)))
        overtime_hours = Decimal(str(values.get("overtime_hours", 0)))
        holiday_work_hours = Decimal(str(values.get("holiday_work_hours", 0)))

        if headcount == 0:
            continue

        wage_day = Decimal(str(job_rates.get(role.job_code, 0)))

        # CalcContext 생성
        context = CalcContext(
            project_name=role.job_name,
            year=2025,
            manpower={role.job_code: headcount},
            wage_rate={role.job_code: wage_day},
            monthly_workdays=work_days,
            daily_work_hours=work_hours,
            weekly_holiday_days=Decimal("4.33"),   # 주휴일수
            annual_leave_days=Decimal("1.25"),     # 연차일수
            overtime_hours=overtime_hours,
            holiday_work_hours=holiday_work_hours,
        )

        # LaborCostCalculator로 계산
        labor_result = LaborCostCalculator(context).calculate()

        # 결과 집계
        total += labor_result["total_labor_cost"]
        insurance_aggregate += labor_result.get("insurance", {})
```

#### 3.1.3 LaborCostCalculator 계산 로직

```python
class LaborCostCalculator:
    """노무비 계산 (상여금, 각종 수당, 퇴직금, 보험료 포함)"""

    def calculate(self) -> dict:
        # 1. 기본급 = 일일임금 × 월근무일수
        base_salary = wage_day * work_days

        # 2. 상여금 = 기본급 × (400% / 12개월)
        bonus = base_salary * Decimal("4.0") / Decimal("12")

        # 3. 주휴수당 = 일일임금 × 주휴일수
        weekly_allowance = wage_day * Decimal("4.33")

        # 4. 연차수당 = 일일임금 × 연차일수
        annual_leave = wage_day * Decimal("1.25")

        # 5. 연장근로수당 = 시간급 × 연장시간 × 1.5배
        overtime = (wage_day / Decimal("8")) * overtime_hours * Decimal("1.5")

        # 6. 휴일근로수당 = 시간급 × 휴일근로시간 × 2.0배
        holiday_work = (wage_day / Decimal("8")) * holiday_work_hours * Decimal("2.0")

        # 7. 통상임금 = 기본급 + 상여금 + 주휴수당 + 연차수당
        ordinary_wage = base_salary + bonus + weekly_allowance + annual_leave

        # 8. 퇴직금 = 통상임금 × (1/12)
        retirement = ordinary_wage / Decimal("12")

        # 9. 인적보험료 계산 (보험료 기준: 기본급 + 제수당 + 상여금)
        insurance_base = base_salary + weekly_allowance + annual_leave + bonus

        ins_indust = insurance_base * Decimal("0.009")    # 산재 0.9%
        ins_pension = insurance_base * Decimal("0.045")   # 국민연금 4.5%
        ins_employ = insurance_base * Decimal("0.0065")   # 고용 0.65%
        ins_health = insurance_base * Decimal("0.03545")  # 건강 3.545%
        ins_longcare = ins_health * Decimal("0.1295")     # 장기요양 12.95%
        ins_wage = insurance_base * Decimal("0.0008")     # 임금채권 0.08%
        ins_asbestos = insurance_base * Decimal("0.00005") # 석면 0.005%

        total_insurance = (ins_indust + ins_pension + ins_employ +
                          ins_health + ins_longcare + ins_wage + ins_asbestos)

        # 10. 월 인건비 = 기본급 + 제수당 + 보험료 + 퇴직금
        labor_subtotal = (base_salary + bonus + weekly_allowance +
                         annual_leave + overtime + holiday_work +
                         total_insurance + retirement)

        # 11. 총 노무비 = 월 인건비 × 인원 × 12개월
        role_total = labor_subtotal * headcount * Decimal("12")

        return {
            "base_salary": base_salary,
            "allowances": bonus + weekly_allowance + annual_leave + overtime + holiday_work,
            "insurance_total": total_insurance,
            "labor_subtotal": labor_subtotal,
            "role_total": role_total,
            "insurance": {
                "industrial_accident": ins_indust,
                "national_pension": ins_pension,
                "employment": ins_employ,
                "health": ins_health,
                "long_term_care": ins_longcare,
                "wage_bond": ins_wage,
                "asbestos": ins_asbestos,
            }
        }
```

### 3.2 경비 계산 (Expense Calculation)

#### 3.2.1 계산 흐름
```
1. 경비 입력 데이터 조회 (scenario_input.input_json → expenses.items)
2. 경비 세부 항목 조회 (expense_sub_item)
3. 인적 보험료 7종 병합 (노무비에서 계산된 값)
4. 항목별 금액 계산
   - 고정비: quantity × unit_price × 12 (연간)
   - 변동비: quantity × unit_price × 인원 × 12
   - 대행비: quantity × unit_price (그대로)
5. 그룹별 합계 산출 (FIXED, VARIABLE, PASSTHROUGH)
```

#### 3.2.2 경비 계산식 (실제 구현)

```python
def _calculate_expenses(
    canonical: dict,
    items: list,
    pricebook: list,
    sub_items_map: dict = None,
    labor_total: int = 0,
    insurance_by_exp_code: dict = None,
    expense_items: list = None,
) -> tuple[list[dict], int, int, int]:
    """
    Args:
        canonical: scenario_input.input_json 데이터
        items: md_expense_item 목록
        pricebook: md_expense_pricebook 목록
        sub_items_map: {exp_code: [sub_items]} 세부 항목 맵
        labor_total: 노무비 합계 (안전관리비 계산용)
        insurance_by_exp_code: 노무비에서 계산된 보험료 7종
        expense_items: 경비 항목 목록 (보험료 이름 조회용)

    Returns:
        (expense_rows, fixed_total, variable_total, passthrough_total)
    """

    inputs = canonical.get("expenses", {}).get("items", {})
    price_map = _price_map(pricebook)
    safety_rate = get_safety_management_rate()

    # 인적 보험료 7종을 세부 항목에 병합
    sub_items_map = dict(sub_items_map) if sub_items_map else {}
    if insurance_by_exp_code and expense_items is not None:
        _merge_labor_insurance_into_sub_items(
            sub_items_map, insurance_by_exp_code, expense_items
        )

    # ExpenseCostCalculator로 계산
    calculator = ExpenseCostCalculator(
        items, inputs, price_map, sub_items_map,
        labor_total=labor_total,
        safety_management_rate=safety_rate,
    )
    result = calculator.calculate()

    # 결과 포맷팅
    rows = []
    for line in result.lines:
        sub_rows = []
        for sl in line.sub_lines:
            sub_rows.append({
                "sub_code": sl.sub_code,
                "sub_name": sl.sub_name,
                "spec": sl.spec,
                "unit": sl.unit,
                "quantity": sl.quantity,
                "unit_price": sl.unit_price,
                "amount": sl.amount,
                "remark": sl.remark,
            })

        rows.append({
            "exp_code": line.exp_code,
            "category": line.group_code,
            "name": line.exp_name,
            "row_total": str(line.row_total),
            "type": category_label(line.category),
            "sub_items": sub_rows,
        })

    return rows, result.fixed_total, result.variable_total, result.passthrough_total
```

#### 3.2.3 인적 보험료 자동 병합

```python
# 노무비 보험료 키 → 경비코드 매핑
LABOR_INSURANCE_TO_EXP_CODE = {
    "industrial_accident": "FIX_INS_INDUST",    # 산재보험료
    "national_pension": "FIX_INS_PENSION",      # 국민연금
    "employment": "FIX_INS_EMPLOY",             # 고용보험료
    "health": "FIX_INS_HEALTH",                 # 건강보험료
    "long_term_care": "FIX_INS_LONGTERM",       # 장기요양
    "wage_bond": "FIX_INS_WAGE",                # 임금채권
    "asbestos": "FIX_INS_ASBESTOS",             # 석면피해
}

def _merge_labor_insurance_into_sub_items(
    sub_items_map: dict,
    insurance_by_exp_code: dict[str, int],
    expense_items: list,
) -> None:
    """인적보험 7개에 대해 노무비 계산값으로 세부 1행씩 병합 (in-place)."""

    item_map = {i.exp_code: i.exp_name for i in expense_items}

    for exp_code, amount in insurance_by_exp_code.items():
        if amount is None:
            continue
        # 세부 항목 1개 생성 (월 단위)
        sub_items_map[exp_code] = [{
            "sub_code": exp_code,
            "sub_name": item_map.get(exp_code, exp_code),
            "spec": "",
            "unit": "원/월",
            "quantity": 1,
            "unit_price": int(amount),
            "amount": int(amount),
            "remark": "노무비에서 계산",
            "sort_order": 0,
            "is_active": 1,
        }]
```

#### 3.2.3 인적 보험료 자동 반영

```python
def update_insurance_expenses(
    scenario_id: str,
    labor_lines: List[LaborJobLine],
    conn: sqlite3.Connection
) -> None:
    """노무비 기반 인적 보험료를 경비 세부 항목에 자동 반영"""

    # 1. 보험료 합계 계산
    total_ins = {
        'FIX_INS_INDUST': sum(line.ins_indust for line in labor_lines),
        'FIX_INS_PENSION': sum(line.ins_pension for line in labor_lines),
        'FIX_INS_EMPLOY': sum(line.ins_employ for line in labor_lines),
        'FIX_INS_HEALTH': sum(line.ins_health for line in labor_lines),
        'FIX_INS_LONGCARE': sum(line.ins_longcare for line in labor_lines),
        'FIX_INS_WAGE_CLAIM': sum(line.ins_wage_claim for line in labor_lines),
        'FIX_INS_ASBESTOS': sum(line.ins_asbestos for line in labor_lines),
    }

    # 2. 경비 세부 항목 업데이트
    for exp_code, total_amount in total_ins.items():
        # 기존 항목 삭제
        conn.execute("""
            DELETE FROM expense_sub_items
            WHERE scenario_id = ? AND exp_code = ?
        """, (scenario_id, exp_code))

        # 새 항목 삽입 (월 단위로 저장)
        monthly_amount = total_amount // 12
        if monthly_amount > 0:
            conn.execute("""
                INSERT INTO expense_sub_items (
                    scenario_id, exp_code, sub_code, sub_name,
                    spec, unit, quantity, unit_price, amount
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scenario_id,
                exp_code,
                'AUTO',
                '자동계산',
                '-',
                '월',
                1,
                monthly_amount,
                monthly_amount
            ))

    conn.commit()
```

### 3.3 집계 계산 (Summary Calculation)

```python
@dataclass
class Aggregator:
    """결과 집계"""
    labor_total: int                  # 노무비 합계
    fixed_expense_total: int          # 고정경비 합계
    variable_expense_total: int       # 변동경비 합계
    passthrough_expense_total: int    # 대행경비 합계
    overhead_cost: int                # 일반관리비
    profit: int                       # 이윤
    grand_total: int                  # 총액 (자동 계산)

    def __post_init__(self):
        # 총액 = 노무비 + 고정경비 + 변동경비 + 대행경비 + 일반관리비 + 이윤
        self.grand_total = (
            self.labor_total +
            self.fixed_expense_total +
            self.variable_expense_total +
            self.passthrough_expense_total +
            self.overhead_cost +
            self.profit
        )

def calculate_result(
    scenario_id: str,
    conn=None,
    overhead_rate: float = 0.0,
    profit_rate: float = 0.0
) -> dict:
    """시나리오 전체 계산 수행"""

    # 1. 데이터 조회
    canonical = get_scenario_input(scenario_id, conn)
    repo = MasterDataRepo(conn)
    job_roles = repo.get_job_roles(scenario_id)
    job_rates = {r.job_code: r.wage_day for r in repo.get_job_rates(scenario_id)}
    expense_items = repo.get_expense_items(scenario_id)
    pricebook = repo.get_expense_pricebook(scenario_id)
    all_sub_items = repo.get_expense_sub_items(scenario_id)

    # 세부 항목 맵 생성
    sub_items_map: dict[str, list] = {}
    for si in all_sub_items:
        sub_items_map.setdefault(si.exp_code, []).append(si)

    # 2. 노무비 계산
    labor_rows, labor_total, job_breakdown, insurance_aggregate = _calculate_labor(
        canonical, job_roles, job_rates
    )

    # 3. 인적 보험료 exp_code별 금액 생성
    insurance_by_exp_code = _build_insurance_by_exp_code(insurance_aggregate)

    # 4. 경비 계산 (보험료 병합 포함)
    expense_rows, fixed_total, variable_total, passthrough_total = _calculate_expenses(
        canonical, expense_items, pricebook, sub_items_map,
        labor_total=labor_total,
        insurance_by_exp_code=insurance_by_exp_code,
        expense_items=expense_items,
    )

    # 5. 일반관리비 및 이윤 계산
    # 일반관리비 기준: 노무비 + 고정경비
    overhead_base = labor_total + fixed_total
    overhead_cost = int(overhead_base * overhead_rate / 100)

    # 이윤 기준: 노무비 + 고정경비 + 일반관리비
    profit_base = labor_total + fixed_total + overhead_cost
    profit = int(profit_base * profit_rate / 100)

    # 6. 집계 객체 생성
    aggregator = Aggregator(
        labor_total=labor_total,
        fixed_expense_total=fixed_total,
        variable_expense_total=variable_total,
        passthrough_expense_total=passthrough_total,
        overhead_cost=overhead_cost,
        profit=profit,
    )

    # 7. 결과 반환 및 스냅샷 저장
    result = {
        "aggregator": aggregator,
        "labor_rows": labor_rows,
        "expense_rows": expense_rows,
        "job_breakdown": job_breakdown,
        "insurance_by_exp_code": insurance_by_exp_code,
    }

    _save_result_snapshot(conn, scenario_id, result)

    return result
```

### 3.4 계산 결과 스냅샷 저장

```python
def _save_result_snapshot(conn, scenario_id: str, result: dict) -> None:
    """계산 결과를 calculation_result 테이블에 JSON으로 저장"""

    snapshot = {
        "aggregator": {
            "labor_total": result["aggregator"].labor_total,
            "fixed_expense_total": result["aggregator"].fixed_expense_total,
            "variable_expense_total": result["aggregator"].variable_expense_total,
            "passthrough_expense_total": result["aggregator"].passthrough_expense_total,
            "overhead_cost": result["aggregator"].overhead_cost,
            "profit": result["aggregator"].profit,
            "grand_total": result["aggregator"].grand_total,
        },
        "labor_rows": result["labor_rows"],
        "expense_rows": result["expense_rows"],
        "job_breakdown": result["job_breakdown"],
        "insurance_by_exp_code": result.get("insurance_by_exp_code") or {},
    }

    payload = json.dumps(snapshot, ensure_ascii=True, default=_json_default)

    conn.execute("""
        INSERT INTO calculation_result (scenario_id, result_json, updated_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT(scenario_id) DO UPDATE SET
          result_json=excluded.result_json,
          updated_at=datetime('now')
    """, (scenario_id, payload))

    conn.commit()
```

---

## 4. UI 컴포넌트 설계 (UI Component Design)

### 4.1 메인 윈도우 구조

```
MainWindow
├── Input Panel (좌측)
│   ├── 기본 정보 입력
│   │   ├── 시나리오명
│   │   ├── 기준연도
│   │   ├── 전용면적
│   │   ├── 일반관리비율
│   │   └── 이윤율
│   ├── 직무별 인원 입력 (JobRoleTable)
│   └── 경비 입력 (ExpenseSubItemTable)
│
└── Results Area (우측)
    ├── Tab 1: 노무비 상세 (LaborDetailTable)
    ├── Tab 2: 경비 상세 (ExpenseDetailTable)
    ├── Tab 3: 요약 (SummaryPanel)
    │   ├── 집계 테이블
    │   └── 도넛 차트
    └── Tab 4: 비교 (ComparePage)
```

### 4.2 시그널-슬롯 아키텍처

#### 4.2.1 자동 계산 흐름

```python
# MainWindow 시그널 연결
def _connect_signals(self):
    """시그널 연결"""

    # 1. 직무별 인원 변경 → 노무비 자동 계산
    self.job_role_table.table.itemChanged.connect(
        self._on_job_role_changed
    )

    # 2. 경비 입력 변경 → 경비 자동 집계
    self.expense_input_table.table.itemChanged.connect(
        self._on_expense_input_changed
    )

    # 3. 기본 정보 변경 → 전체 재계산
    self.input_panel.value_changed.connect(
        self._on_basic_info_changed
    )

def _on_job_role_changed(self):
    """직무별 인원 변경 시 자동 계산"""

    # 1. 테이블 편집 커밋
    commit_table_edit(self.job_role_table.table)

    # 2. 입력 데이터 수집
    job_inputs = self.job_role_table.get_job_inputs()
    values = self.input_panel.get_values()
    scenario_id = self._sanitize_filename(values.get("scenario_name"))
    base_year = values.get("base_year", 2024)

    # 3. 노무비 계산
    conn = get_connection()
    try:
        labor_rows = calculate_labor_rows(
            job_inputs, scenario_id, base_year, conn
        )

        # 4. 노무비 상세 표시
        self.labor_detail.update_rows(labor_rows)

        # 5. 인적 보험료 경비 반영
        update_insurance_expenses(scenario_id, labor_rows, conn)

        # 6. 경비 상세 갱신
        self._refresh_expense_detail()

        # 7. 요약 갱신
        self._refresh_summary()

    finally:
        conn.close()
```

#### 4.2.2 시나리오 불러오기 데이터 보존

```python
def load_scenario(self, scenario_id: str):
    """시나리오 불러오기 (기존 입력 데이터 보존)"""

    conn = get_connection()
    try:
        # 1. 기본 정보 로드
        scenario = get_scenario(scenario_id, conn)
        if not scenario:
            return

        # 2. 기본 정보 패널 업데이트 (시그널 블록)
        self.input_panel.blockSignals(True)
        self.input_panel.set_values({
            "scenario_name": scenario.scenario_name,
            "base_year": scenario.base_year,
            "total_area": scenario.total_area,
            "overhead_rate": scenario.overhead_rate,
            "profit_rate": scenario.profit_rate
        })
        self.input_panel.blockSignals(False)

        # 3. 직무별 인원 로드 (기존 데이터 병합)
        job_inputs_db = get_job_inputs(scenario_id, conn)
        job_inputs_ui = self.job_role_table.get_job_inputs()

        # DB 데이터 우선, 없으면 UI 현재값 유지
        merged_inputs = {}
        for job_input in job_inputs_ui:
            merged_inputs[job_input.job_code] = job_input

        for job_input in job_inputs_db:
            merged_inputs[job_input.job_code] = job_input

        # 4. 직무별 인원 테이블 업데이트 (시그널 블록)
        self.job_role_table.table.blockSignals(True)
        self.job_role_table.set_job_inputs(list(merged_inputs.values()))
        self.job_role_table.table.blockSignals(False)

        # 5. 경비 입력 로드 (기존 데이터 보존하지 않고 덮어쓰기)
        expense_sub_items = get_expense_sub_items(scenario_id, conn)
        self.expense_input_table.table.blockSignals(True)
        self.expense_input_table.load_items(expense_sub_items)
        self.expense_input_table.table.blockSignals(False)

        # 6. 자동 계산 트리거
        self._on_job_role_changed()

    finally:
        conn.close()
```

### 4.3 테이블 위젯 설계

#### 4.3.1 JobRoleTable (직무별 인원 입력)

```python
class JobRoleTable(QWidget):
    """직무별 인원 입력 테이블"""

    def __init__(self):
        super().__init__()
        self.table = QTableWidget()
        self._setup_table()

    def _setup_table(self):
        """테이블 초기화"""

        # 컬럼: 직무명, 인원, 근무일수
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            "직무명", "인원", "근무일수"
        ])

        # 17개 표준 직무 행 생성
        standard_jobs = get_standard_jobs()
        self.table.setRowCount(len(standard_jobs))

        for row, job in enumerate(standard_jobs):
            # 직무명 (읽기 전용)
            item_name = QTableWidgetItem(job.job_name)
            item_name.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item_name.setData(Qt.ItemDataRole.UserRole, job.job_code)
            self.table.setItem(row, 0, item_name)

            # 인원 (편집 가능, 숫자만)
            item_headcount = QTableWidgetItem("0")
            item_headcount.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.table.setItem(row, 1, item_headcount)

            # 근무일수 (편집 가능, 기본값 365)
            item_workdays = QTableWidgetItem("365")
            item_workdays.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.table.setItem(row, 2, item_workdays)

    def get_job_inputs(self) -> List[JobInput]:
        """현재 입력값 조회"""

        job_inputs = []
        for row in range(self.table.rowCount()):
            job_code = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            headcount = int(self.table.item(row, 1).text() or 0)
            workdays = int(self.table.item(row, 2).text() or 365)

            job_inputs.append(JobInput(
                job_code=job_code,
                headcount=headcount,
                workdays=workdays
            ))

        return job_inputs
```

#### 4.3.2 LaborDetailTable (노무비 상세)

```python
class LaborDetailTable(QWidget):
    """노무비 상세 테이블 (읽기 전용)"""

    def __init__(self):
        super().__init__()
        self.table = QTableWidget()
        self._setup_table()

    def _setup_table(self):
        """테이블 초기화"""

        # 컬럼: 직무명, 인원, 일수, 기본급, 제수당,
        #       산재, 국민연금, 고용, 건강, 장기요양, 임금채권, 석면, 산정금액
        columns = [
            "직무명", "인원", "일수", "기본급", "제수당",
            "산재", "국민연금", "고용", "건강", "장기요양",
            "임금채권", "석면", "산정금액"
        ]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        # 모든 셀 읽기 전용
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

    def update_rows(self, labor_rows: List[LaborJobLine]):
        """노무비 행 업데이트"""

        # 인원이 있는 행만 표시
        active_rows = [r for r in labor_rows if r.headcount > 0]

        self.table.setRowCount(len(active_rows) + 1)  # +1 for 합계 행

        # 데이터 행
        for row, labor in enumerate(active_rows):
            self.table.setItem(row, 0, self._create_item(labor.job_name))
            self.table.setItem(row, 1, self._create_item(labor.headcount))
            self.table.setItem(row, 2, self._create_item(labor.workdays))
            self.table.setItem(row, 3, self._create_item(labor.base_wage))
            self.table.setItem(row, 4, self._create_item(labor.allowances))
            self.table.setItem(row, 5, self._create_item(labor.ins_indust))
            self.table.setItem(row, 6, self._create_item(labor.ins_pension))
            self.table.setItem(row, 7, self._create_item(labor.ins_employ))
            self.table.setItem(row, 8, self._create_item(labor.ins_health))
            self.table.setItem(row, 9, self._create_item(labor.ins_longcare))
            self.table.setItem(row, 10, self._create_item(labor.ins_wage_claim))
            self.table.setItem(row, 11, self._create_item(labor.ins_asbestos))
            self.table.setItem(row, 12, self._create_item(labor.total_amount))

        # 합계 행
        total_row = len(active_rows)
        self._add_total_row(total_row, active_rows)

    def _add_total_row(self, row: int, labor_rows: List[LaborJobLine]):
        """합계 행 추가"""

        # 합계 라벨
        item_label = QTableWidgetItem("합계")
        item_label.setBackground(QColor("#f0f0f0"))
        item_label.setFont(QFont("맑은 고딕", 9, QFont.Weight.Bold))
        self.table.setItem(row, 0, item_label)

        # 합계 계산
        totals = {
            "total_amount": sum(r.total_amount for r in labor_rows)
        }

        # 합계 표시
        item_total = self._create_item(totals["total_amount"])
        item_total.setBackground(QColor("#f0f0f0"))
        item_total.setFont(QFont("맑은 고딕", 9, QFont.Weight.Bold))
        self.table.setItem(row, 12, item_total)
```

---

## 5. 파일 구조 및 모듈 (File Structure & Modules)

### 5.1 디렉토리 구조

```
src/
├── main.py                     # 애플리케이션 진입점
├── logging_config.py           # 로깅 설정
├── version.py                  # 버전 정보
│
├── domain/                     # 비즈니스 로직
│   ├── __init__.py
│   ├── db.py                   # 데이터베이스 연결
│   ├── migration_runner.py     # 마이그레이션 실행
│   │
│   ├── calculator/             # 계산 로직
│   │   ├── __init__.py
│   │   ├── labor.py            # 노무비 계산
│   │   └── expense.py          # 경비 계산
│   │
│   ├── context/                # 계산 컨텍스트
│   │   ├── __init__.py
│   │   └── calc_context.py     # InsuranceContext 등
│   │
│   ├── masterdata/             # 마스터 데이터
│   │   ├── __init__.py
│   │   ├── repo.py             # 데이터 접근 (Repository)
│   │   └── service.py          # 서비스 로직
│   │
│   ├── result/                 # 결과 집계
│   │   ├── __init__.py
│   │   └── service.py          # 집계 서비스
│   │
│   ├── scenario_input/         # 시나리오 입출력
│   │   ├── __init__.py
│   │   └── service.py          # 시나리오 저장/불러오기
│   │
│   ├── migrations/             # SQL 마이그레이션
│   │   └── *.sql
│   │
│   └── constants/              # 상수 정의
│       ├── __init__.py
│       └── rounding.py         # 반올림 규칙
│
├── ui/                         # UI 컴포넌트
│   ├── __init__.py
│   ├── main_window.py          # 메인 윈도우
│   ├── input_panel.py          # 입력 패널
│   ├── job_role_table.py       # 직무별 인원 테이블
│   ├── expense_sub_item_table.py # 경비 입력 테이블
│   ├── labor_detail_table.py   # 노무비 상세 테이블
│   ├── expense_detail_table.py # 경비 상세 테이블
│   ├── summary_panel.py        # 요약 패널
│   ├── donut_chart.py          # 도넛 차트
│   ├── state.py                # UI 상태 관리
│   ├── theme.py                # UI 테마
│   ├── validation.py           # 입력 검증
│   │
│   └── compare/                # 비교 페이지
│       ├── __init__.py
│       ├── compare_page.py     # 비교 페이지
│       ├── compare_table.py    # 비교 테이블
│       └── scenario_selector.py # 시나리오 선택기
│
└── utils/                      # 유틸리티
    ├── __init__.py
    └── path_helper.py          # 경로 헬퍼
```

### 5.2 주요 모듈 책임

| 모듈 | 책임 | 주요 함수/클래스 |
|------|------|------------------|
| **domain/db.py** | DB 연결 관리 | `get_connection()` |
| **domain/migration_runner.py** | 마이그레이션 실행 | `run_migrations()` |
| **domain/calculator/labor.py** | 노무비 계산 | `calculate_labor_for_job()`, `LaborJobLine` |
| **domain/calculator/expense.py** | 경비 계산 | `calculate_total_expense()`, `ExpenseLine` |
| **domain/masterdata/repo.py** | 마스터 데이터 조회 | `get_job_roles()`, `get_wages()` |
| **domain/masterdata/service.py** | 마스터 데이터 관리 | `apply_seed_if_needed()` |
| **domain/result/service.py** | 집계 계산 | `calculate_summary()` |
| **domain/scenario_input/service.py** | 시나리오 IO | `save_scenario()`, `load_scenario()` |
| **ui/main_window.py** | 메인 윈도우 | `MainWindow`, 시그널 연결 |
| **ui/job_role_table.py** | 직무별 인원 입력 | `JobRoleTable.get_job_inputs()` |
| **ui/labor_detail_table.py** | 노무비 상세 표시 | `LaborDetailTable.update_rows()` |

---

## 6. 에러 처리 및 검증 (Error Handling & Validation)

### 6.1 입력 검증

```python
# ui/validation.py

def validate_scenario_name(name: str) -> Tuple[bool, str]:
    """시나리오명 검증"""
    if not name or not name.strip():
        return False, "시나리오명을 입력하세요."
    if len(name) > 100:
        return False, "시나리오명은 100자 이하로 입력하세요."
    return True, ""

def validate_year(year: int) -> Tuple[bool, str]:
    """기준연도 검증"""
    if year < 2023 or year > 2026:
        return False, "기준연도는 2023~2026 사이여야 합니다."
    return True, ""

def validate_headcount(headcount: int) -> Tuple[bool, str]:
    """인원 수 검증"""
    if headcount < 0:
        return False, "인원 수는 0 이상이어야 합니다."
    if headcount > 9999:
        return False, "인원 수는 9999 이하로 입력하세요."
    return True, ""

def validate_workdays(workdays: int) -> Tuple[bool, str]:
    """근무일수 검증"""
    if workdays < 1 or workdays > 365:
        return False, "근무일수는 1~365 사이여야 합니다."
    return True, ""
```

### 6.2 예외 처리

```python
# ui/main_window.py

def _on_job_role_changed(self):
    """직무별 인원 변경 시 자동 계산 (에러 처리 포함)"""

    try:
        # 1. 입력 데이터 검증
        job_inputs = self.job_role_table.get_job_inputs()
        for job_input in job_inputs:
            valid, msg = validate_headcount(job_input.headcount)
            if not valid:
                raise ValueError(msg)
            valid, msg = validate_workdays(job_input.workdays)
            if not valid:
                raise ValueError(msg)

        # 2. 계산 수행
        conn = get_connection()
        try:
            labor_rows = calculate_labor_rows(...)
            self.labor_detail.update_rows(labor_rows)
            self.status_bar.showMessage("✓ 노무비 자동계산 완료", 3000)

        finally:
            conn.close()

    except ValueError as e:
        # 입력 검증 오류
        self.status_bar.showMessage(f"⚠ {str(e)}", 5000)
        QMessageBox.warning(self, "입력 오류", str(e))

    except sqlite3.Error as e:
        # 데이터베이스 오류
        error_msg = f"데이터베이스 오류: {str(e)}"
        logging.exception(error_msg)
        self.status_bar.showMessage(f"⚠ {error_msg}", 5000)
        QMessageBox.critical(self, "DB 오류", error_msg)

    except Exception as e:
        # 기타 오류
        error_msg = f"노무비 계산 중 오류: {str(e)}"
        logging.exception(error_msg)
        self.status_bar.showMessage(f"⚠ {error_msg}", 5000)
        QMessageBox.critical(self, "오류", f"{error_msg}\n\n자세한 내용은 로그를 확인하세요.")
```

### 6.3 데이터 무결성 보장

```python
# domain/scenario_input/service.py

def save_scenario(
    scenario_id: str,
    scenario_data: dict,
    job_inputs: List[JobInput],
    conn: sqlite3.Connection
) -> None:
    """시나리오 저장 (트랜잭션 보장)"""

    try:
        # 트랜잭션 시작
        conn.execute("BEGIN")

        # 1. 시나리오 정보 저장/업데이트
        conn.execute("""
            INSERT INTO scenarios (scenario_id, scenario_name, base_year, ...)
            VALUES (?, ?, ?, ...)
            ON CONFLICT(scenario_id) DO UPDATE SET
                scenario_name = excluded.scenario_name,
                base_year = excluded.base_year,
                ...
                updated_at = CURRENT_TIMESTAMP
        """, (...))

        # 2. 직무별 인원 저장
        conn.execute("DELETE FROM job_inputs WHERE scenario_id = ?", (scenario_id,))
        for job_input in job_inputs:
            if job_input.headcount > 0:
                conn.execute("""
                    INSERT INTO job_inputs (scenario_id, job_code, headcount, workdays)
                    VALUES (?, ?, ?, ?)
                """, (scenario_id, job_input.job_code, job_input.headcount, job_input.workdays))

        # 커밋
        conn.commit()

    except Exception as e:
        # 롤백
        conn.rollback()
        raise
```

---

## 7. 성능 최적화 (Performance Optimization)

### 7.1 시그널 블록킹

```python
# 대량 데이터 업데이트 시 시그널 임시 차단

def load_scenario(self, scenario_id: str):
    """시나리오 불러오기 (최적화)"""

    # 시그널 차단
    self.job_role_table.table.blockSignals(True)
    self.expense_input_table.table.blockSignals(True)

    try:
        # 데이터 로드 및 UI 업데이트
        ...
    finally:
        # 시그널 복원
        self.job_role_table.table.blockSignals(False)
        self.expense_input_table.table.blockSignals(False)

    # 한 번만 자동 계산 트리거
    self._on_job_role_changed()
```

### 7.2 DB 인덱스 활용

```sql
-- 자주 조회되는 컬럼에 인덱스 생성

CREATE INDEX idx_wages_year ON md_wages(year);
CREATE INDEX idx_wages_job_code ON md_wages(job_code);
CREATE INDEX idx_job_inputs_scenario ON job_inputs(scenario_id);
CREATE INDEX idx_expense_sub_scenario ON expense_sub_items(scenario_id);
```

### 7.3 계산 결과 캐싱

```python
# ui/main_window.py

def __init__(self):
    ...
    self.last_labor_rows = []  # 마지막 계산 결과 캐시
    self.last_summary = None   # 마지막 집계 결과 캐시

def _on_job_role_changed(self):
    """노무비 계산 및 결과 캐싱"""

    labor_rows = calculate_labor_rows(...)
    self.last_labor_rows = labor_rows  # 캐싱

    # 경비 계산 시 재사용
    update_insurance_expenses(..., self.last_labor_rows, ...)
```

---

## 8. 테스트 전략 (Testing Strategy)

### 8.1 단위 테스트

```python
# tests/test_labor_calculator.py

def test_calculate_labor_for_job():
    """노무비 계산 단위 테스트"""

    # Given
    job_code = "MGR01"
    headcount = 2
    workdays = 365
    base_year = 2024

    # When
    result = calculate_labor_for_job(
        job_code, headcount, workdays, base_year, test_conn
    )

    # Then
    assert result.job_code == "MGR01"
    assert result.headcount == 2
    assert result.workdays == 365
    assert result.base_wage == 290410
    assert result.total_amount > 0

def test_insurance_calculation():
    """보험료 계산 정확성 테스트"""

    # Given
    base_wage = 290410

    # When
    ins_indust = int(base_wage * 0.0165)
    ins_pension = int(base_wage * 0.045)

    # Then
    assert ins_indust == 4791
    assert ins_pension == 13068
```

### 8.2 통합 테스트

```python
# tests/test_integration.py

def test_full_calculation_flow():
    """전체 계산 흐름 통합 테스트"""

    # Given: 시나리오 생성
    scenario_id = "test_scenario"
    job_inputs = [
        JobInput("MGR01", 2, 365),
        JobInput("ENG01", 1, 365)
    ]

    conn = get_connection()
    try:
        # When: 계산 실행
        summary = calculate_summary(
            scenario_id=scenario_id,
            base_year=2024,
            overhead_rate=18.5,
            profit_rate=15.0,
            conn=conn
        )

        # Then: 결과 검증
        assert summary.total_labor > 0
        assert summary.total_expense > 0
        assert summary.grand_total > summary.subtotal

    finally:
        conn.close()
```

### 8.3 UI 테스트

```python
# tests/test_ui.py

def test_job_role_table_input():
    """직무별 인원 테이블 입력 테스트"""

    # Given
    app = QApplication([])
    table = JobRoleTable()

    # When: 인원 입력
    table.table.setItem(0, 1, QTableWidgetItem("5"))
    table.table.setItem(0, 2, QTableWidgetItem("365"))

    # Then: 입력값 조회
    job_inputs = table.get_job_inputs()
    assert job_inputs[0].headcount == 5
    assert job_inputs[0].workdays == 365
```

---

## 9. 배포 전략 (Deployment Strategy)

### 9.1 패키징 (PyInstaller)

```bash
# auto_fm.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data/wages_master.json', 'data'),
        ('src/domain/migrations/*.sql', 'src/domain/migrations')
    ],
    hiddenimports=['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets'],
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
    [],
    exclude_binaries=True,
    name='auto_fm',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Windows GUI 모드
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'  # 애플리케이션 아이콘
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='auto_fm'
)
```

### 9.2 설치 프로그램 (Inno Setup)

```ini
; installer.iss

[Setup]
AppName=auto_fm 시설관리 원가 계산
AppVersion=1.0.0
DefaultDirName={pf}\auto_fm
DefaultGroupName=auto_fm
OutputBaseFilename=auto_fm_setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\auto_fm\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\auto_fm"; Filename: "{app}\auto_fm.exe"
Name: "{commondesktop}\auto_fm"; Filename: "{app}\auto_fm.exe"

[Run]
Filename: "{app}\auto_fm.exe"; Description: "프로그램 실행"; Flags: nowait postinstall skipifsilent
```

### 9.3 빌드 스크립트

```batch
REM build.bat

@echo off
echo ========================================
echo auto_fm 빌드 시작
echo ========================================

REM 1. 가상환경 활성화
call venv\Scripts\activate

REM 2. 의존성 설치
pip install -r requirements.txt

REM 3. PyInstaller 빌드
pyinstaller auto_fm.spec --clean

REM 4. Inno Setup 컴파일
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss

echo ========================================
echo 빌드 완료!
echo 설치 파일: installer_output\auto_fm_setup.exe
echo ========================================
pause
```

---

## 10. 마이그레이션 계획 (Migration Plan)

### 10.1 초기 마이그레이션

```sql
-- src/domain/migrations/20260101_01_init_schema.sql

-- 직무 마스터
CREATE TABLE IF NOT EXISTS md_job_roles (
    job_code TEXT PRIMARY KEY,
    job_name TEXT NOT NULL,
    job_type TEXT,
    sort_order INTEGER,
    is_standard BOOLEAN DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 임금 마스터
CREATE TABLE IF NOT EXISTS md_wages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_code TEXT NOT NULL,
    year INTEGER NOT NULL,
    base_wage INTEGER NOT NULL,
    allowances INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_code) REFERENCES md_job_roles(job_code),
    UNIQUE(job_code, year)
);

-- 경비 항목 마스터
CREATE TABLE IF NOT EXISTS md_expense_items (
    exp_code TEXT PRIMARY KEY,
    exp_name TEXT NOT NULL,
    group_code TEXT NOT NULL,
    sort_order INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 시나리오
CREATE TABLE IF NOT EXISTS scenarios (
    scenario_id TEXT PRIMARY KEY,
    scenario_name TEXT NOT NULL,
    base_year INTEGER DEFAULT 2024,
    total_area REAL,
    overhead_rate REAL DEFAULT 18.5,
    profit_rate REAL DEFAULT 15.0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 직무별 인원 입력
CREATE TABLE IF NOT EXISTS job_inputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id TEXT NOT NULL,
    job_code TEXT NOT NULL,
    headcount INTEGER DEFAULT 0,
    workdays INTEGER DEFAULT 365,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (job_code) REFERENCES md_job_roles(job_code),
    UNIQUE(scenario_id, job_code)
);

-- 경비 세부 항목
CREATE TABLE IF NOT EXISTS expense_sub_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id TEXT NOT NULL,
    exp_code TEXT NOT NULL,
    sub_code TEXT,
    sub_name TEXT,
    spec TEXT,
    unit TEXT,
    quantity REAL DEFAULT 0,
    unit_price INTEGER DEFAULT 0,
    amount INTEGER DEFAULT 0,
    remark TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (exp_code) REFERENCES md_expense_items(exp_code)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_wages_year ON md_wages(year);
CREATE INDEX IF NOT EXISTS idx_wages_job_code ON md_wages(job_code);
CREATE INDEX IF NOT EXISTS idx_job_inputs_scenario ON job_inputs(scenario_id);
CREATE INDEX IF NOT EXISTS idx_expense_sub_scenario ON expense_sub_items(scenario_id);
CREATE INDEX IF NOT EXISTS idx_expense_sub_code ON expense_sub_items(exp_code);
```

### 10.2 Seed 데이터

```sql
-- src/domain/migrations/20260101_02_seed_job_roles.sql

-- 표준 직무 코드 (17개)
INSERT OR IGNORE INTO md_job_roles (job_code, job_name, job_type, sort_order) VALUES
('MGR01', '관리감독자', '관리', 1),
('ENG01', '공장장', '기술', 2),
('TECH01', '기능공(특급)', '기술', 3),
('TECH02', '기능공(고급)', '기술', 4),
('TECH03', '기능공(중급)', '기술', 5),
('TECH04', '기능공(초급)', '기술', 6),
('SEMI01', '반기능공(중급)', '기술', 7),
('SEMI02', '반기능공(초급)', '기술', 8),
('HELPER01', '조력공', '기술', 9),
('LABOR01', '노무공', '기술', 10),
('ELEC01', '전기공(중급)', '기술', 11),
('ELEC02', '전기공(초급)', '기술', 12),
('PLUMB01', '배관공(중급)', '기술', 13),
('PLUMB02', '배관공(초급)', '기술', 14),
('GUARD01', '경비원', '관리', 15),
('CLEAN01', '청소원', '관리', 16),
('DRIVER01', '운전원', '관리', 17);
```

---

## 11. 다음 단계 (Next Steps)

### 11.1 구현 완료 확인

- [x] 데이터베이스 스키마
- [x] 마이그레이션 시스템
- [x] 노무비 계산 로직
- [x] 경비 계산 로직
- [x] 인적 보험료 자동 반영
- [x] UI 컴포넌트
- [x] 시나리오 저장/불러오기
- [ ] **자동 계산 동작 확인 및 버그 수정** ← 현재 단계

### 11.2 Gap Analysis 준비

- 이 Design 문서와 실제 구현 코드를 비교
- Match Rate 계산
- 미구현 기능 또는 불일치 항목 식별

### 11.3 다음 PDCA 단계

```bash
/pdca analyze auto_fm    # Gap 분석 실행
/pdca iterate auto_fm    # Gap 해결 (필요 시)
/pdca report auto_fm     # 완료 보고서 작성
```

---

**작성자**: PDCA System
**최종 수정**: 2026-02-14
**다음 단계**: `/pdca analyze auto_fm` - Gap 분석 실행

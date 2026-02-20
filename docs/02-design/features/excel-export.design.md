# excel-export Design Document

> **Summary**: auto_fm_fin.xlsx 동일 양식 Excel 내보내기 (템플릿 기반 데이터 주입)
>
> **Project**: auto_fm
> **Date**: 2026-02-16
> **Status**: Draft
> **Planning Doc**: [excel-export.plan.md](../../01-plan/features/excel-export.plan.md)

---

## 1. Overview

### 1.1 Design Goals

- `src/auto_fm_fin.xlsx`를 템플릿으로 사용하여 계산 결과를 주입하고, 원본과 동일한 서식의 Excel 파일 생성
- Phase 1 MVP: 핵심 8개 시트 (갑지, 용역원가집계, 용역원가(24~26년), 인건비집계, 경비집계, 일반관리비, 이윤)
- 단일 연도 계산 결과를 3개년에 동일 복사 (Plan 결정사항)

### 1.2 Design Principles

- **템플릿 보존**: openpyxl로 원본을 열어 데이터 셀만 교체 → 서식(병합, 폰트, 테두리, 배경색) 자동 보존
- **셀 좌표 명시**: 시트별 데이터 주입 좌표를 상수로 정의하여 유지보수 용이
- **확장 가능**: Phase 2~5 시트를 sheet_writer 추가만으로 확장

---

## 2. Architecture

### 2.1 Component Diagram

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  UI Button   │────▶│  ExcelExporter   │────▶│  Output .xlsx   │
│ (main_window)│     │  (orchestrator)  │     │  (사용자 저장)   │
└──────────────┘     └────────┬─────────┘     └─────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │  Template Loader   │
                    │  (auto_fm_fin.xlsx)│
                    └─────────┬──────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │ cover_writer │ │ summary_     │ │ labor_       │
     │ (갑지)       │ │ writer       │ │ writer       │
     └──────────────┘ │ (용역원가)   │ │ (인건비집계) │
                      └──────────────┘ └──────────────┘
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │ expense_     │ │ overhead_    │ │ (Phase 2+)   │
     │ writer       │ │ writer       │ │              │
     │ (경비집계)   │ │ (관리비/이윤)│ │              │
     └──────────────┘ └──────────────┘ └──────────────┘
```

### 2.2 Data Flow

```
calculate_result() → snapshot dict
                         │
                         ▼
              ExcelExporter.__init__(template_path, snapshot)
                         │
                         ▼
              wb = openpyxl.load_workbook(template_path)
                         │
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
     write_갑지()  write_용역원가() write_인건비()  ...
     (ws['갑지'])  (ws['용역원가..'])  (ws[인건비집계])
           │             │             │
           └─────────────┼─────────────┘
                         ▼
              wb.save(output_path)
```

### 2.3 Dependencies

| Component | Depends On | Purpose |
|-----------|-----------|---------|
| ExcelExporter | openpyxl | Excel 읽기/쓰기 |
| ExcelExporter | result/service.py | calculate_result snapshot |
| ExcelExporter | Aggregator | 총액/비율 데이터 |
| UI button handler | ExcelExporter | 내보내기 실행 |

---

## 3. Data Model

### 3.1 Snapshot Structure (calculate_result 반환값)

```python
snapshot = {
    "aggregator": {
        "labor_total": int,              # 인건비 합계
        "fixed_expense_total": int,      # 고정경비 합계
        "variable_expense_total": int,   # 변동경비 합계
        "passthrough_expense_total": int, # 대행비 합계
        "overhead_cost": int,            # 일반관리비
        "profit": int,                   # 이윤
        "grand_total": int,              # 총계
    },
    "labor_rows": [
        {
            "job_code": str,
            "role": str,            # 직종명
            "headcount": int,
            "base_salary": int,     # 기본급 (월)
            "allowances": int,      # 제수당 (월)
            "bonus": int,           # 상여금 (월)
            "retirement": int,      # 퇴직금 (월)
            "labor_subtotal": int,  # 인건비 소계 (월)
            "role_total": int,      # 총액
        },
    ],
    "expense_rows": [
        {
            "exp_code": str,
            "category": str,        # 그룹 코드 (fixed/variable/passthrough)
            "name": str,            # 경비 항목명
            "row_total": str,       # 월 합계 (str)
            "type": str,            # 카테고리 라벨
            "sub_items": [...],
        },
    ],
    "insurance_by_exp_code": {
        "FIX_INS_INDUST": int,      # 산재보험료
        "FIX_INS_PENSION": int,     # 국민연금
        "FIX_INS_EMPLOY": int,      # 고용보험료
        "FIX_INS_HEALTH": int,      # 건강보험료
        "FIX_INS_LONGTERM": int,    # 장기요양보험료
        "FIX_INS_WAGE": int,        # 임금채권보장보험료
        "FIX_INS_ASBESTOS": int,    # 석면피해구제분담금
    },
}
```

### 3.2 추가 파생 데이터 (ExcelExporter 내부 계산)

```python
# 연간 = 월간 × 12
annual_labor_total = aggregator["labor_total"] * 12
annual_fixed = aggregator["fixed_expense_total"] * 12
annual_variable = aggregator["variable_expense_total"] * 12
annual_passthrough = aggregator["passthrough_expense_total"] * 12

# 순용역원가 = 인건비 + 고정경비
net_service_cost = aggregator["labor_total"] + aggregator["fixed_expense_total"]

# 고정비 소계 (보험+복리후생+기타고정)
# 변동비 소계
# 대행비 소계 — 이상 expense_rows에서 category별 합산
```

---

## 4. Phase 1 시트별 셀 매핑

### 4.1 갑지 (예정원가예산서)

시트명: `갑지` (sheetnames[4])

| 셀 | 데이터 | 소스 |
|----|--------|------|
| L11 | 총액(3개년) | `grand_total * 12 * 3` (천원 절사) |
| L14 | 1차분(2024년) | `grand_total * 12` (천원 절사) |
| L17 | 2차분(2025년) | `grand_total * 12` (동일 복사) |
| L20 | 3차분(2026년) | `grand_total * 12` (동일 복사) |

- 숫자 포맷: `"금"#,##0"원"` (기존 서식 유지)
- 3개년 동일 복사 (Plan 결정)

### 4.2 용역원가집계

시트명: `용역원가집계` (sheetnames[8])

| 셀 | 데이터 | 소스 |
|----|--------|------|
| B8 | 1차 월간용역비 | `grand_total` |
| C8 | 위탁기간(월) | `12` |
| D8 | 1차 연간용역비 | `grand_total * 12` |
| B9 | 2차 월간용역비 | `grand_total` (동일 복사) |
| C9 | 위탁기간(월) | `12` |
| D9 | 2차 연간용역비 | `grand_total * 12` |
| B10 | 3차 월간용역비 | `grand_total` (동일 복사) |
| C10 | 위탁기간(월) | `12` |
| D10 | 3차 연간용역비 | `grand_total * 12` |
| D12 | 총 용역비 | `grand_total * 12 * 3` |

- 숫자 포맷: `_-* #,##0_-` (회계 포맷)

### 4.3 용역원가(24년/25년/26년) — 연도별 원가계산서

3개 시트 동일 구조, 각 시트별 행 오프셋 차이 있음.

시트명: `용역원가(24년)` (idx 9), `용역원가(25년) ` (idx 10, 뒤 공백), `용역원가(26년)` (idx 11)

**행 구조 매핑** (24년 / 25년 기준):

| 항목 | 24년 셀 | 25년 셀 | 26년 셀 | 데이터 소스 |
|------|---------|---------|---------|-------------|
| **인건비** | | | | |
| 기본급 | G7/H7 | G7/H7 | G7/H7 | `sum(base_salary)` / `×12` |
| 제수당소계 | G11/H11 | G11/H11 | G11/H11 | `sum(allowances)` / `×12` |
| 상여금 | G12/H12 | G12/H12 | G12/H12 | `sum(bonus)` / `×12` |
| 퇴직충당금 | G13/H13 | G13/H13 | G13/H13 | `sum(retirement)` / `×12` |
| 인건비계 | G14/H14 | G14/H14 | G14/H14 | `labor_total` / `×12` |
| **보험료** | | | | |
| 산재보험료 | G15/H15 | G15/H15 | G15/H15 | `ins[FIX_INS_INDUST]` |
| 국민연금 | G16/H16 | G16/H16 | G16/H16 | `ins[FIX_INS_PENSION]` |
| 고용보험료 | G17/H17 | G17/H17 | G17/H17 | `ins[FIX_INS_EMPLOY]` |
| 건강보험료 | G18/H18 | G18/H18 | G18/H18 | `ins[FIX_INS_HEALTH]` |
| 장기요양보험 | G19/H19 | G19/H19 | G19/H19 | `ins[FIX_INS_LONGTERM]` |
| 임금채권보장 | G20/H20 | G20/H20 | G20/H20 | `ins[FIX_INS_WAGE]` |
| 석면피해구제 | G21/H21 | G21/H21 | G21/H21 | `ins[FIX_INS_ASBESTOS]` |
| **복리후생비** | G22/H22 | G22/H22 | G22/H22 | expense `FIX_WELFARE_*` 합 |
| **기타고정경비** | | | | |
| 안전관리비 | G23/H23 | G23/H23 | G23/H23 | expense `FIX_SAFETY` |
| 교육훈련비 | G24/H24 | G24/H24 | G24/H24 | expense `FIX_TRAINING` |
| 소모품비 | G25/H25 | G25/H25 | G25/H25 | expense `FIX_SUPPLIES` |
| 출장여비 | G26/H26 | G26/H26 | G26/H26 | expense `FIX_TRAVEL` |
| 통신비 | G27/H27 | G27/H27 | G27/H27 | expense `FIX_TELECOM` |

**하단 구조** (24년 vs 25년 행 오프셋):

| 항목 | 24년 행 | 25년 행 | 26년 행 | G열(월) | H열(연) |
|------|---------|---------|---------|---------|---------|
| 고정경비계 | 28 | 29 | 28 | `fixed_expense_total` | `×12` |
| 순용역원가 | 29 | 30 | 29 | `labor+fixed` | `×12` |
| 일반관리비 | 30 | 31 | 30 | `overhead_cost` | `×12` |
| 이윤 | 31 | 32 | 31 | `profit` | `×12` |
| 용역원가 | 32 | 33 | 32 | `net+oh+profit` | `×12` |
| 인건비충당 | 33 | 34 | 33 | `용역원가×10%` | `×12` |
| 고정비소비합 | 34 | 35 | 34 | `용역원가+충당` | `×12` |
| **변동경비** | | | | | |
| 소모자재비 | 35→C | 36→C | 35→C | expense by code | `×12` |
| 수선유지비 | 36→C | 37→C | 36→C | expense by code | `×12` |
| 측정검사수수료 | 37→C | 38→C | 37→C | expense by code | `×12` |
| 안전점검대행비 | 38→C | 39→C | 38→C | expense by code | `×12` |
| 차량유지비 | 39→C | 40→C | 39→C | expense by code | `×12` |
| 보안관리비 | 40→C | 41→C | 40→C | expense by code | `×12` |
| 수집운반비 | 41→C | 42→C | 41→C | expense by code | `×12` |
| 변동경비합 | 42→C | 43→C | 42→C | `variable_total` | `×12` |
| 변동용역원가 | 43→C | 44→C | 43→C | 변동합 | `×12` |
| 변동인건비충당 | 44→C | 45→C | 44→C | `변동×10%` | `×12` |
| 변동소비합 | 45→C | 46→C | 45→C | 변동+충당 | `×12` |
| **대행비** | | | | | |
| 전력비 | 46→C | 47→C | 46→C | expense by code | `×12` |
| 수도광열비 | 47→C | 48→C | 47→C | expense by code | `×12` |
| 시설물보험료 | 48→C | 49→C | 48→C | expense by code | `×12` |
| 대행비합 | 49→C | 50→C | 49→C | `passthrough_total` | `×12` |
| 고정+변동합 | 50→B | 51→B | 50→B | 고정소비합+변동소비합 | `×12` |
| **총계** | 51→A | 52→A | 51→A | `grand_total` | `×12` |

**구현 접근**: 시트별 행 오프셋 상수 정의

```python
YEARLY_SHEET_ROW_OFFSETS = {
    "용역원가(24년)":  {"fixed_subtotal": 28, "variable_start": 35, "total": 51},
    "용역원가(25년) ": {"fixed_subtotal": 29, "variable_start": 36, "total": 52},
    "용역원가(26년)":  {"fixed_subtotal": 28, "variable_start": 35, "total": 51},
}
```

### 4.4 인건비집계

시트명: `인건비집계` (sheetnames[13])

**구조**: 행 5-7 = 헤더, 행 8~24 = 직종별 데이터 (최대 17행), 행 25 = 합계

**열 구조**:

| 열 | 내용 | 비고 |
|----|------|------|
| A | 직종 그룹 | (시설관리, 환경관리, 경비원 등) |
| B | 직책명 | (시설과장, 전기기사 등) |
| D | 등급 | (특급/고급/중급/초급) |
| F | 기본급 - 1인당(1개월) | `base_salary ÷ headcount` |
| G | 기본급 - 근무인원 | `headcount` |
| H | 기본급 - 금액 | `base_salary` |
| I | 제수당 - 1인당 | `allowances ÷ headcount` |
| J | 제수당 - 근무인원 | `headcount` |
| K | 제수당 - 금액 | `allowances` |
| L | 상여금 - 1인당 | `bonus ÷ headcount` |
| M | 상여금 - 근무인원 | `headcount` |
| N | 상여금 - 금액 | `bonus` |
| O | 퇴직금 - 1인당 | `retirement ÷ headcount` |
| P | 퇴직금 - 근무인원 | `headcount` |
| Q | 퇴직금 - 금액 | `retirement` |
| R | 합계 - 1인당 | `labor_subtotal ÷ headcount` |
| S | 합계 - 근무인원 | `headcount` |
| T | 합계 - 금액 | `labor_subtotal` |

**데이터 행**: 행 8~24 → `labor_rows` 배열 순서대로 매핑 (headcount > 0인 항목만)

**합계 행 (25)**:

| 셀 | 내용 |
|----|------|
| G25 | 총 인원 |
| H25 | 기본급 합계 |
| K25 | 제수당 합계 |
| N25 | 상여금 합계 |
| Q25 | 퇴직금 합계 |
| T25 | 인건비 합계 |

### 4.5 경비집계

시트명: `경비집계` (sheetnames[27])

**구조**: 행 5-6 = 헤더, 행 7~35 = 데이터

| 행 | 항목 | F열(월액) | 소스 |
|----|------|-----------|------|
| **고정경비** | | | |
| 7 | 산재보험료 | F7 | `ins[FIX_INS_INDUST]` |
| 8 | 국민연금 | F8 | `ins[FIX_INS_PENSION]` |
| 9 | 고용보험료 | F9 | `ins[FIX_INS_EMPLOY]` |
| 10 | 건강보험료 | F10 | `ins[FIX_INS_HEALTH]` |
| 11 | 장기요양보험 | F11 | `ins[FIX_INS_LONGTERM]` |
| 12 | 임금채권보장 | F12 | `ins[FIX_INS_WAGE]` |
| 13 | 석면피해구제 | F13 | `ins[FIX_INS_ASBESTOS]` |
| 14 | 보험료소계 | F14 | `sum(insurance)` |
| 15 | 복리후생비 | F15 | expense `FIX_WEL_*` 합 |
| 16 | 안전관리비 | F16 | expense `FIX_SAFETY` |
| 17 | 교육훈련비 | F17 | expense `FIX_TRAINING` |
| 18 | 소모품비 | F18 | expense `FIX_SUPPLIES` |
| 19 | 출장여비 | F19 | expense `FIX_TRAVEL` |
| 20 | 통신비 | F20 | expense `FIX_TELECOM` |
| 22 | 고정경비계 | F22 | `fixed_expense_total` |
| **변동경비** | | | |
| 23 | 소모자재비 | F23 | expense by code |
| 24 | 수선유지비 | F24 | expense by code |
| 25 | 측정검사수수료 | F25 | expense by code |
| 26 | 안전점검대행비 | F26 | expense by code |
| 27 | 차량유지비 | F27 | expense by code |
| 28 | 보안관리비 | F28 | expense by code |
| 29 | 수집운반비 | F29 | expense by code |
| 30 | 변동경비계 | F30 | `variable_total + passthrough_total` or sum |
| **대행비** | | | |
| 31 | 전력비 | F31 | expense by code |
| 32 | 수도광열비 | F32 | expense by code |
| 33 | 시설물보험료 | F33 | expense by code |
| 34 | 대행비계 | F34 | `passthrough_total` |
| **합계** | | | |
| 35 | 총합계 | F35 | `fixed + variable + passthrough` |

### 4.6 일반관리비

시트명: `일반관리비` (sheetnames[56])

| 셀 | 데이터 | 소스 |
|----|--------|------|
| B8 | 인건비 | `labor_total` (월) |
| C8 | 고정경비 | `fixed_expense_total` (월) |
| D8 | 계 | `labor_total + fixed_expense_total` |
| E8 | 비율(%) | `overhead_rate` (e.g. 9) |
| F8 | 금액 | `overhead_cost` (월) |
| F10 | 계 (동일) | `overhead_cost` |

### 4.7 이윤

시트명: `이윤` (sheetnames[59])

| 셀 | 데이터 | 소스 |
|----|--------|------|
| B8 | 인건비 | `labor_total` (월) |
| C8 | 고정경비 | `fixed_expense_total` (월) |
| D8 | 일반관리비 | `overhead_cost` (월) |
| E8 | 계 | `labor + fixed + overhead` |
| F8 | 비율(%) | `profit_rate` (e.g. 10) |
| G8 | 금액 | `profit` (월) |
| G10 | 계 (동일) | `profit` |

---

## 5. Module Design

### 5.1 File Structure

```
src/domain/export/
├── __init__.py
├── excel_exporter.py          # 메인 ExcelExporter 클래스
└── cell_maps.py               # 시트별 셀 좌표 상수/매핑
```

### 5.2 ExcelExporter Class

```python
# src/domain/export/excel_exporter.py

from pathlib import Path
import openpyxl
from openpyxl.workbook import Workbook

class ExcelExporter:
    """시나리오 집계 결과를 auto_fm_fin.xlsx 양식으로 내보내기."""

    def __init__(self, template_path: Path, snapshot: dict,
                 overhead_rate: float = 9.0, profit_rate: float = 10.0):
        """
        Args:
            template_path: auto_fm_fin.xlsx 경로
            snapshot: calculate_result 반환값 또는 DB 스냅샷
            overhead_rate: 일반관리비율 (%)
            profit_rate: 이윤율 (%)
        """
        self.wb: Workbook = openpyxl.load_workbook(template_path)
        self.snapshot = snapshot
        self.overhead_rate = overhead_rate
        self.profit_rate = profit_rate
        self._agg = snapshot["aggregator"]
        self._labor_rows = snapshot["labor_rows"]
        self._expense_rows = snapshot["expense_rows"]
        self._insurance = snapshot.get("insurance_by_exp_code", {})

    def export(self, output_path: Path) -> Path:
        """모든 Phase 1 시트에 데이터 주입 후 저장."""
        self._write_gapji()
        self._write_service_cost_summary()
        self._write_yearly_cost_sheet("용역원가(24년)")
        self._write_yearly_cost_sheet("용역원가(25년) ")
        self._write_yearly_cost_sheet("용역원가(26년)")
        self._write_labor_summary()
        self._write_expense_summary()
        self._write_overhead()
        self._write_profit()
        self.wb.save(output_path)
        return output_path

    # --- 갑지 ---
    def _write_gapji(self) -> None: ...

    # --- 용역원가집계 ---
    def _write_service_cost_summary(self) -> None: ...

    # --- 용역원가(XX년) ---
    def _write_yearly_cost_sheet(self, sheet_name: str) -> None: ...

    # --- 인건비집계 ---
    def _write_labor_summary(self) -> None: ...

    # --- 경비집계 ---
    def _write_expense_summary(self) -> None: ...

    # --- 일반관리비 ---
    def _write_overhead(self) -> None: ...

    # --- 이윤 ---
    def _write_profit(self) -> None: ...

    # --- helpers ---
    def _get_ws(self, name: str):
        """시트명으로 worksheet 반환 (이름에 공백 등 포함 대응)."""
        for sn in self.wb.sheetnames:
            if sn.strip() == name.strip():
                return self.wb[sn]
        raise KeyError(f"Sheet not found: {name}")

    def _expense_monthly(self, exp_code: str) -> int:
        """expense_rows에서 특정 exp_code의 월 합계 반환."""
        for row in self._expense_rows:
            if row["exp_code"] == exp_code:
                return int(float(row["row_total"]))
        return 0

    def _set_cell(self, ws, coord: str, value) -> None:
        """기존 서식을 보존하면서 값만 설정."""
        ws[coord].value = value
```

### 5.3 cell_maps.py (셀 좌표 상수)

```python
# src/domain/export/cell_maps.py

# 갑지 셀 좌표
GAPJI = {
    "total_3year": "L11",
    "year1": "L14",
    "year2": "L17",
    "year3": "L20",
}

# 용역원가집계 셀 좌표
SERVICE_COST_SUMMARY = {
    "y1_monthly": "B8", "y1_months": "C8", "y1_annual": "D8",
    "y2_monthly": "B9", "y2_months": "C9", "y2_annual": "D9",
    "y3_monthly": "B10", "y3_months": "C10", "y3_annual": "D10",
    "grand_total": "D12",
}

# 용역원가(XX년) 공통 셀 (G열=월, H열=연)
# 상단 인건비+보험 영역 (행 7~22)은 3개 시트 동일
YEARLY_COMMON_ROWS = {
    "base_salary": 7,
    "allowances_subtotal": 11,
    "bonus": 12,
    "retirement": 13,
    "labor_total": 14,
    "ins_indust": 15,
    "ins_pension": 16,
    "ins_employ": 17,
    "ins_health": 18,
    "ins_longterm": 19,
    "ins_wage": 20,
    "ins_asbestos": 21,
    "welfare": 22,
    "safety": 23,
    "training": 24,
    "supplies": 25,
    "travel": 26,
    "telecom": 27,
}

# 하단 행 오프셋 (시트별 차이)
YEARLY_BOTTOM_OFFSETS = {
    "용역원가(24년)": {
        "fixed_subtotal": 28,
        "net_service": 29,
        "overhead": 30,
        "profit": 31,
        "service_cost": 32,
        "contingency": 33,
        "fixed_grand": 34,
        "var_start": 35,  # 변동경비 시작행
        "var_subtotal": 42,
        "var_service": 43,
        "var_contingency": 44,
        "var_grand": 45,
        "pass_start": 46,  # 대행비 시작행
        "pass_subtotal": 49,
        "all_grand": 50,
        "total": 51,
    },
    "용역원가(25년) ": {
        "fixed_subtotal": 29,
        "net_service": 30,
        "overhead": 31,
        "profit": 32,
        "service_cost": 33,
        "contingency": 34,
        "fixed_grand": 35,
        "var_start": 36,
        "var_subtotal": 43,
        "var_service": 44,
        "var_contingency": 45,
        "var_grand": 46,
        "pass_start": 47,
        "pass_subtotal": 50,
        "all_grand": 51,
        "total": 52,
    },
    "용역원가(26년)": {
        "fixed_subtotal": 28,
        "net_service": 29,
        "overhead": 30,
        "profit": 31,
        "service_cost": 32,
        "contingency": 33,
        "fixed_grand": 34,
        "var_start": 35,
        "var_subtotal": 42,
        "var_service": 43,
        "var_contingency": 44,
        "var_grand": 45,
        "pass_start": 46,
        "pass_subtotal": 49,
        "all_grand": 50,
        "total": 51,
    },
}

# 인건비집계 열 매핑
LABOR_SUMMARY_COLS = {
    "base_per_person": "F", "base_headcount": "G", "base_amount": "H",
    "allow_per_person": "I", "allow_headcount": "J", "allow_amount": "K",
    "bonus_per_person": "L", "bonus_headcount": "M", "bonus_amount": "N",
    "retire_per_person": "O", "retire_headcount": "P", "retire_amount": "Q",
    "total_per_person": "R", "total_headcount": "S", "total_amount": "T",
}
LABOR_SUMMARY_DATA_START_ROW = 8
LABOR_SUMMARY_TOTAL_ROW = 25

# 경비집계 행→exp_code 매핑
EXPENSE_SUMMARY_ROWS = {
    7: "FIX_INS_INDUST",
    8: "FIX_INS_PENSION",
    9: "FIX_INS_EMPLOY",
    10: "FIX_INS_HEALTH",
    11: "FIX_INS_LONGTERM",
    12: "FIX_INS_WAGE",
    13: "FIX_INS_ASBESTOS",
    # 14 = 보험소계 (계산)
    15: "FIX_WEL",       # 복리후생비 합산
    16: "FIX_SAFETY",
    17: "FIX_TRAINING",
    18: "FIX_SUPPLIES",
    19: "FIX_TRAVEL",
    20: "FIX_TELECOM",
    # 22 = 고정경비계
    23: "VAR_CONSUMABLE",
    24: "VAR_REPAIR",
    25: "VAR_INSPECTION",
    26: "VAR_SAFETY_AGENCY",
    27: "VAR_VEHICLE",
    28: "VAR_SECURITY",
    29: "VAR_COLLECTION",
    # 30 = 변동경비계
    31: "PASS_ELECTRICITY",
    32: "PASS_WATER",
    33: "PASS_FACILITY_INS",
    # 34 = 대행비계
    # 35 = 합계
}
EXPENSE_SUMMARY_COL = "F"

# 일반관리비
OVERHEAD_CELLS = {
    "labor": "B8", "fixed": "C8", "sum": "D8",
    "rate": "E8", "amount": "F8", "total": "F10",
}

# 이윤
PROFIT_CELLS = {
    "labor": "B8", "fixed": "C8", "overhead": "D8",
    "sum": "E8", "rate": "F8", "amount": "G8", "total": "G10",
}
```

---

## 6. UI Integration

### 6.1 Export Button Handler

`src/ui/main_window.py`의 기존 `_export_details_excel_impl` 대체 또는 새 메뉴 추가.

```python
def _export_full_excel(self):
    """auto_fm_fin.xlsx 양식으로 전체 Excel 내보내기."""
    from src.domain.export.excel_exporter import ExcelExporter
    from pathlib import Path

    # 1. 현재 시나리오의 최신 스냅샷 가져오기
    snapshot = get_result_snapshot(self.current_scenario_id, conn)
    if snapshot is None:
        # 집계 실행 필요
        QMessageBox.warning(self, "알림", "집계를 먼저 실행해주세요.")
        return

    # 2. 저장 경로 선택
    path, _ = QFileDialog.getSaveFileName(
        self, "Excel 내보내기", "용역원가.xlsx",
        "Excel Files (*.xlsx)"
    )
    if not path:
        return

    # 3. 템플릿 기반 내보내기
    template_path = Path(__file__).parent.parent / "auto_fm_fin.xlsx"
    exporter = ExcelExporter(
        template_path=template_path,
        snapshot=snapshot,
        overhead_rate=self.overhead_rate,
        profit_rate=self.profit_rate,
    )
    exporter.export(Path(path))
    QMessageBox.information(self, "완료", f"Excel 파일이 저장되었습니다:\n{path}")
```

---

## 7. Error Handling

| 상황 | 처리 |
|------|------|
| 템플릿 파일 없음 | FileNotFoundError → UI 알림 |
| 시트명 불일치 | `_get_ws()` 에서 KeyError → 해당 시트 건너뛰기 + 로그 |
| 스냅샷 없음 | UI에서 "집계 먼저 실행" 안내 |
| 숫자 변환 오류 | try/except → 0 기본값 + 로그 |
| 파일 저장 실패 | PermissionError → UI 알림 (파일 닫고 재시도) |

---

## 8. Test Plan

### 8.1 Test Cases

- [ ] 갑지 총액이 `grand_total × 12 × 3`과 일치
- [ ] 용역원가집계 D12가 3개년 합계와 일치
- [ ] 용역원가(25년) 인건비계(G14)가 labor_rows 합과 일치
- [ ] 인건비집계 합계행(T25)이 labor_total과 일치
- [ ] 경비집계 합계행(F35)이 fixed+variable+passthrough와 일치
- [ ] 일반관리비 F8이 overhead_cost와 일치
- [ ] 이윤 G8이 profit과 일치
- [ ] 원본 서식(병합셀, 폰트, 테두리) 보존 확인

### 8.2 수동 검증

- 생성된 xlsx를 Excel에서 열어 원본과 시각적 비교
- 숫자 포맷(천단위 콤마, 회계 포맷) 확인

---

## 9. Implementation Order

1. `src/domain/export/__init__.py` 생성
2. `src/domain/export/cell_maps.py` — 셀 좌표 상수 정의
3. `src/domain/export/excel_exporter.py` — ExcelExporter 클래스:
   - `_write_gapji()` (가장 단순 → 동작 검증)
   - `_write_service_cost_summary()`
   - `_write_overhead()`, `_write_profit()`
   - `_write_labor_summary()`
   - `_write_expense_summary()`
   - `_write_yearly_cost_sheet()` (가장 복잡)
4. `src/ui/main_window.py` — export 버튼 핸들러 연결

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-02-16 | Initial draft - Phase 1 MVP design |

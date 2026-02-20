# Plan: auto_fm_fin.xlsx 동일 양식 Excel 내보내기

## 1. 개요

**Feature**: `excel-export`
**목표**: 현재 시나리오 집계 결과를 `auto_fm_fin.xlsx`와 동일한 양식(62개 시트, 셀 병합, 서식, 레이아웃)으로 Excel 파일 출력
**우선순위**: High
**현재 상태**: 기존 `_export_details_excel_impl`은 단순 데이터 4시트만 출력 (Summary, Labor Detail, Expense Detail, 노무비_직종상세)

---

## 2. auto_fm_fin.xlsx 분석 결과

### 2.1 전체 구조 (62시트)

| 그룹 | 시트명 | 설명 | 데이터 소스 |
|------|--------|------|-------------|
| **표지/갑지** | 표지 | 표지(사업명, 날짜, 발주처) | 시나리오 메타 |
| | 갑지 | 예정원가예산서 (총액, 1~3차분) | aggregator |
| | 간지# | 구분 페이지 | 정적 |
| **총괄** | 설명서 | 설계내역서 항목번호/품명/수량/단가 (2254행) | 전체 계산 결과 |
| | 36개월총괄 | 3년 총괄 원가내역서 (고정비·변동비·관리비·이윤) | 연도별 aggregator |
| | 용역원가집계 | 1~3차 월간/연간 용역비 | aggregator |
| | 용역원가(24년) | 2024년 용역원가계산서 (49행) | year=2024 결과 |
| | 용역원가(25년) | 2025년 용역원가계산서 (52행) | year=2025 결과 |
| | 용역원가(26년) | 2026년 용역원가계산서 (51행) | year=2026 결과 |
| | 2023년계약원가 비교 | 이전 계약 비교용 | 비교 데이터 |
| **인건비** | 인건비집계 | 직종별 기본급/제수당/상여금/퇴직금 집계 (29열) | labor_rows |
| | 제수당집계 | 년차/연장/휴일수당 집계 (21열) | labor_rows |
| | 단위당인건비 | 직책별 1인당 인건비 산출 (377행, 직종수×블록) | labor_job_line |
| | 엔지니어노임 | 엔지니어링 기술자 노임단가표 | masterdata (wages) |
| | 월기본급 | 직종별 월기본급 산출 (43행) | wage_rates |
| | 기본급추정 | 기본급 추정 산출표 | wage_rates |
| | 인건비산정기준 | 산정 기준 설명 | 정적/설정 |
| | 일급분개 | 일급 분개표 (248행, 직종수×월별) | labor_job_line |
| | 보험료산정기준 | 보험료 산정 기준 | 정적/설정 |
| | 산재비율 | 산재보험 요율 | masterdata |
| **인원/근무** | 투입인원 | 적용직종 및 근무형태 | job_roles |
| | 근무일수 | 직종별 근무일수 | scenario_input |
| | 2024년 달력 | 달력 (공휴일 표시) | 정적/설정 |
| | 가동시간 | 연간 가동시간 | scenario_input |
| | 기간현황 | 용역 기간 현황 | 시나리오 메타 |
| **경비-고정** | 경비집계 | 경비 항목 총괄 집계 | expense_rows |
| | 고정)인적보험료집계 | 7종 보험료 집계 (31열) | insurance_aggregate |
| | 고정)인적보험료 | 직종별 보험료 상세 (153행) | insurance × job_roles |
| | 고정)복리후생비집계 | 복리후생비 4항목 집계 (33열) | expense_rows (welfare) |
| | 고정)피복비 | 피복비 상세 | sub_items (FIX_WEL_CLOTH) |
| | 고정)식대 | 식대 상세 | sub_items (FIX_WEL_MEAL) |
| | 고정)건강검진비 | 건강검진비 상세 | sub_items (FIX_WEL_CHECKUP) |
| | 고정)의약품 | 의약품비 상세 | sub_items (FIX_WEL_MEDICINE) |
| | 고정)안전관리비 | 안전관리비 상세 | sub_items (FIX_SAFETY) |
| | 고정)교육훈련비 | 교육훈련비 상세 | sub_items (FIX_TRAINING) |
| | 고정)소모품비 | 소모품비 상세 | sub_items (FIX_SUPPLIES) |
| | 고정)출장여비 | 출장여비 상세 | sub_items (FIX_TRAVEL) |
| | 운임 | 운임 상세 | 별도 계산 |
| | 고정)통신비 | 통신비 상세 | sub_items (FIX_TELECOM) |
| **경비-변동** | 변동)소모자재비 | 소모자재비 상세 | sub_items |
| | 변동)수선유지비 | 수선유지비 상세 (33열 확장) | sub_items |
| | 변동)측정검사수수료 | 측정검사 상세 | sub_items |
| | 변동)안전점검대행비 | 안전점검 상세 | sub_items |
| | 변동)차량유지비 | 차량유지비 상세 | sub_items |
| | 변동)보안관리비 | 보안관리비 상세 | sub_items |
| | 변동)수집운반비 | 수집운반비 상세 (16열) | sub_items |
| | 수집운반_세금과공과 | 세금과공과 부속표 | sub_items |
| | 기타경비 | 기타경비 상세 | sub_items |
| | 수리수선비 | 수리수선비 (65열 대형 시트) | sub_items |
| | 감가상각비 | 감가상각비 | sub_items |
| **대행비** | 변동-대)전력비 | 전력비 상세 | sub_items |
| | 전력사용량 | 전력사용량 산출 (43열) | sub_items |
| | 변동-대)수도광열비 | 수도광열비 상세 | sub_items |
| | 변동-대)시설물보험료 | 시설물보험료 상세 | sub_items |
| **관리비/이윤** | 일반관리비 | 일반관리비 산출 | aggregator |
| | 일반관리비율 | 일반관리비율 산출 | 설정 |
| | 일반-시행규칙 | 시행규칙 참조 | 정적 |
| | 이윤 | 이윤 산출 | aggregator |
| | 이윤율 | 이윤비율표 | 정적 |
| **분석** | 기업분석 | 기업분석표 (160행) | 정적/참고 |
| **시스템** | ECSYSTEM | 시스템 메타데이터 | 정적 |
| | 차수별용역비 | 차수별 요약 | aggregator |
| | 용역원가집계 (중복) | 용역원가 요약 테이블 | aggregator |

### 2.2 핵심 서식 특성

- **셀 병합**: 대부분의 시트에 2~240개의 병합 셀 사용
- **숫자 포맷**: `#,##0` (천단위 콤마), `_-* #,##0_-` (회계 포맷)
- **정렬**: center, distributed (균등분할), left/right 혼합
- **헤더 구조**: 대부분 Row 1-6 = 제목/번호/헤더, Row 7+ = 데이터
- **비고 컬럼**: 법규 참조, 표 번호 참조 등 주석 포함
- **공통 패턴**: `[ 표 : N ]` 형식의 표 번호 체계

---

## 3. 구현 전략

### 3.1 접근 방식: **템플릿 기반 (Template + Data Injection)**

원본 `auto_fm_fin.xlsx`를 **템플릿으로 사용**하여 데이터만 주입하는 방식 채택.

**이유**:
- 62시트의 서식(셀 병합, 너비, 높이, 폰트, 테두리, 배경색)을 코드로 재현하는 것은 비효율적
- 원본 파일을 openpyxl로 열어서 데이터 셀만 교체하면 서식이 보존됨
- 정적 시트(법규 참조, 달력 등)는 그대로 유지

### 3.2 시트 분류 (구현 우선순위)

**Phase 1 - 핵심 시트 (MVP)**:
1. 갑지 (총액 표시)
2. 용역원가집계 (1~3차 월간/연간)
3. 용역원가(24~26년) (연도별 상세 원가계산서)
4. 인건비집계 (직종별 인건비)
5. 경비집계 (경비 항목 총괄)
6. 일반관리비 / 이윤

**Phase 2 - 인건비 상세**:
7. 단위당인건비 (377행 직종별 블록)
8. 제수당집계
9. 월기본급
10. 일급분개

**Phase 3 - 경비 상세**:
11. 고정)인적보험료집계 / 고정)인적보험료
12. 고정)복리후생비집계
13. 고정 경비 개별 시트 (피복비~통신비, 10개)
14. 변동 경비 개별 시트 (소모자재비~수집운반비, 10개)

**Phase 4 - 대행비/참고**:
15. 대행비 시트 (전력비, 수도광열비, 시설물보험료)
16. 투입인원, 근무일수, 가동시간
17. 36개월총괄

**Phase 5 - 나머지**:
18. 표지, 간지
19. 설명서 (2254행)
20. 정적 참고 시트 (달력, 법규, 기업분석 등)

### 3.3 아키텍처

```
src/
├── domain/
│   └── export/
│       ├── __init__.py
│       ├── excel_exporter.py      # 메인 엑스포터 클래스
│       ├── template_loader.py     # 템플릿 로드 + 데이터 매핑
│       ├── sheet_writers/
│       │   ├── __init__.py
│       │   ├── cover_writer.py        # 표지/갑지
│       │   ├── summary_writer.py      # 총괄/용역원가
│       │   ├── labor_writer.py        # 인건비 관련
│       │   ├── expense_writer.py      # 경비 관련
│       │   ├── overhead_writer.py     # 일반관리비/이윤
│       │   └── reference_writer.py    # 투입인원/근무일수 등
│       └── cell_mapping.py        # 시트별 셀 좌표 ↔ 데이터 필드 매핑
├── ui/
│   └── main_window.py             # export_excel_button 핸들러 교체
└── templates/
    └── auto_fm_fin_template.xlsx  # 원본 복사 (서식 전용 템플릿)
```

### 3.4 핵심 클래스 설계

```python
class ExcelExporter:
    """시나리오 집계 결과를 auto_fm_fin.xlsx 양식으로 내보내기"""

    def __init__(self, template_path: Path, snapshot: dict, scenario_meta: dict):
        self.wb = openpyxl.load_workbook(template_path)
        self.snapshot = snapshot        # calculation_result JSON
        self.meta = scenario_meta       # 시나리오명, 기간, 발주처 등

    def export(self, output_path: Path) -> None:
        """모든 시트에 데이터 주입 후 저장"""
        self._write_cover()         # 표지/갑지
        self._write_summary()       # 총괄/용역원가
        self._write_labor()         # 인건비 관련
        self._write_expenses()      # 경비 관련
        self._write_overhead()      # 일반관리비/이윤
        self._write_reference()     # 참고 시트
        self.wb.save(output_path)
```

---

## 4. 데이터 소스 매핑

### 4.1 필요 데이터 (calculation_result snapshot)

| 데이터 | 현재 snapshot 포함 여부 | 비고 |
|--------|----------------------|------|
| aggregator (총액) | O | labor_total, expense totals, overhead, profit |
| labor_rows (직종별) | O | role, headcount, base_salary, allowances, bonus, retirement |
| expense_rows | O | category, name, row_total, sub_items |
| insurance_by_exp_code | O | 7종 보험료 |
| job_breakdown | △ | build_job_breakdown_rows로 생성 가능 |
| 연도별 분리 결과 | X | **추가 필요**: 연도별(24/25/26) 개별 계산 |
| 제수당 상세 | △ | labor_job_line에서 추출 가능 |
| 월기본급 상세 | X | **추가 필요**: wage_rates 기반 산출 |
| 일급분개 | X | **추가 필요**: 일급 × 일수 분개 |
| 보험료 직종별 상세 | X | **추가 필요**: 직종×보험종류 교차표 |

### 4.2 추가 개발 필요 항목

1. **연도별 계산 분리**: 현재 단일 시나리오만 계산 → 3개년 분리 계산 지원
2. **보험료 직종별 교차표**: 직종×보험종류별 금액 매트릭스
3. **일급분개표 데이터**: 직종×월별 일급 분개 데이터
4. **시나리오 메타데이터**: 사업명, 발주처, 날짜 등 UI 입력 필드

---

## 5. 리스크 및 고려사항

| 리스크 | 영향 | 대응 |
|--------|------|------|
| openpyxl 템플릿 로드 시 일부 서식 손실 | 중 | 테스트 후 손실 서식 수동 복원 코드 추가 |
| 행 수가 가변적인 시트 (단위당인건비 등) | 고 | 행 삽입/삭제 로직 + 병합 셀 재설정 필요 |
| 3개년 분리 계산 미구현 | 고 | Phase 1에서는 단일년도 × 3 복사, Phase 2에서 실제 분리 |
| 대형 시트 (수리수선비 65열) | 중 | 셀 매핑 자동화 스크립트 활용 |
| 설명서 2254행 자동 생성 | 중 | 별도 행 생성 로직 필요 |

---

## 6. 작업 추정

| Phase | 시트 수 | 핵심 작업 |
|-------|---------|-----------|
| Phase 1 (MVP) | 8 | 템플릿 로더, 갑지/용역원가/인건비집계/경비집계/관리비/이윤 |
| Phase 2 | 4 | 단위당인건비(가변행), 제수당집계, 월기본급, 일급분개 |
| Phase 3 | 22 | 경비 세부 시트 (고정10 + 변동10 + 보험료집계2) |
| Phase 4 | 8 | 대행비, 투입인원, 근무일수, 가동시간, 36개월총괄 |
| Phase 5 | 20 | 표지, 설명서, 정적 참고 시트 |

---

## 7. 결정 사항 (사용자 확인 완료)

1. **3개년 처리**: 단일 연도 결과를 3개년에 동일하게 복사 → 빠른 구현
2. **정적 시트**: 원본 그대로 유지 (달력, 법규, 기업분석 등 포함)
3. **템플릿**: `src/auto_fm_fin.xlsx`를 그대로 템플릿으로 사용
4. **우선순위**: Phase 1 MVP (핵심 8시트)부터 시작

---

## 8. Phase 1 MVP 구현 범위

**목표 시트 (8개)**:
1. `갑지` - 예정원가예산서 (총액, 1~3차분 금액)
2. `용역원가집계` - 월간/연간 용역비 집계
3. `용역원가(24년)` - 2024년 용역원가계산서
4. `용역원가(25년)` - 2025년 용역원가계산서
5. `용역원가(26년)` - 2026년 용역원가계산서
6. `인건비집계` - 직종별 기본급/제수당/상여금/퇴직금
7. `경비집계` - 경비 항목 총괄
8. `일반관리비` + `이윤` - 관리비/이윤 산출

**Phase 1 산출물**:
- `src/domain/export/excel_exporter.py` (메인 엑스포터)
- `src/domain/export/sheet_writers/` (시트별 writer)
- `src/domain/export/cell_mapping.py` (셀 좌표 매핑)
- UI `export_excel_button` 핸들러 교체

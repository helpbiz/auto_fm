# 직무별 인원입력 개선 제안

## 1. 현재 구조에서 반복되는 문제 원인

### 1.1 직무코드 컬럼의 이중 표현
- **COL_JOB_CODE(0)**에 `setItem(code_item)` 후 `setCellWidget(combo)`를 사용함.
- 같은 셀에 **Item**과 **Widget**이 공존 → 읽을 때는 `cellWidget`이 있으면 콤보 값, 없으면 item 텍스트를 봐야 함.
- `_ensure_row_items`, `_force_editable_full`에서 **cellWidget 있는 셀은 건너뛰기** 로직이 필수이고, 실수로 `setItem(row, 0, ...)`를 호출하면 콤보가 사라짐.
- Enter 키로 "다음 셀" 이동 시 `editItem(self.item(row, COL_JOB_CODE))` 호출 → 0번 컬럼은 위젯이라 편집 동작이 일반 셀과 달라 키보드 동선이 불안정함.

### 1.2 데이터 소스가 테이블 한 곳뿐
- **읽기**: `get_job_inputs()`가 매번 테이블을 돌며 `_get_job_code(row)`(콤보 vs 아이템 분기), `safe_get(col)` 호출.
- **쓰기**: `load_roles` / `set_job_inputs`가 테이블에 직접 쓰고, 콤보는 별도 `_install_job_code_combo`로 설치.
- 테이블 상태(로우 개수, 아이템 존재 여부, 콤보 존재 여부)에 따라 `set_job_inputs`에서 `self.table.item(row, COL_WORK_DAYS)`가 None일 수 있어 예외 가능.

### 1.3 변경 시마다 무거운 연산
- `itemChanged`가 **셀 단위**로 발생 → 직무별 인원 입력이 바뀔 때마다 메인 윈도우 콜백 → 노무비/보험/요약 재계산.
- 입력 중에도 계속 재계산되어, 수십 행일 때 지연·깜빡임 가능.

### 1.4 디버그/훅 코드
- `attach_table_debug_log`, `hook_suspicious_methods`, `_force_editable_full` 내부의 `QTimer.singleShot` 로그 등이 항상 동작.
- 프로덕션에서도 실행되며, 실수로 편집 트리거 등이 바뀌면 디버그 로그만 보이고 원인 파악이 어려움.

---

## 2. 개선 방향 (에러 없이 적용하려는 순서)

### 2.1 1단계: 직무코드 컬럼을 Delegate로 통일 (최우선)

**목표**: COL_JOB_CODE도 **QTableWidgetItem 하나**만 두고, 편집 시에만 콤보가 뜨게 함.

**방법**:
- `setCellWidget(row, COL_JOB_CODE, combo)` 제거.
- COL_JOB_CODE 전용 **QStyledItemDelegate** 추가:
  - `createEditor(parent, option, index)` → `QComboBox` 반환 (현재 _available_roles 기준으로 항목 채움).
  - `setEditorData(editor, index)` → 현재 셀 텍스트(직무코드)를 콤보 currentText에 맞춤.
  - `setModelData(editor, model, index)` → 콤보 `currentText()`를 셀에 저장.
  - `displayText(value, locale)` → 코드 그대로 표시 (또는 코드+직무명은 paint에서 처리).
- `load_roles`에서는 COL_JOB_CODE에 대해 `setItem(row, COL_JOB_CODE, QTableWidgetItem(job_code))`만 하고, `_install_job_code_combo` 호출 제거.
- `_get_job_code(row)`는 `self.table.item(row, COL_JOB_CODE).text()` 만 사용.
- `_ensure_row_items`, `_force_editable_full`에서 **cellWidget 건너뛰기** 제거 가능.
- `keyPressEvent`에서 COL_JOB_CODE 셀도 일반 셀처럼 `editItem(item)` 가능.

**효과**: 직무코드 때문에 생기던 “콤보 덮어쓰기 / 편집 불가 / 키 이동 꼬임” 제거.

---

### 2.2 2단계: 내부 모델 도입 (선택, 구조 정리용)

**목표**: 테이블은 “보기/입력용 뷰”만 담당하고, **진짜 데이터는 리스트/딕셔너리 한 곳**에서만 관리.

**방법**:
- `JobRoleTable` 내부에 `_rows: list[dict]` 유지. 한 행: `{ "job_code", "job_name", "grade", "work_days", "work_hours", "overtime_hours", "holiday_work_hours", "headcount" }`.
- `load_roles(roles, ...)` → `_rows`를 roles 기준으로 채우고, 테이블은 `_rows`를 반영해 그리기.
- `get_job_inputs()` → `_rows`에서 `{ job_code: { work_days, work_hours, ... } }` 형태로 반환 (테이블에서 직접 읽지 않음).
- `set_job_inputs(job_inputs)` → `_rows`만 갱신한 뒤, 테이블 전체를 `_rows` 기준으로 다시 그리기.
- 셀 편집이 끝날 때(`commitData` 또는 `itemChanged`) 해당 행의 `_rows[row_idx]`만 갱신. 직무코드 변경 시에는 `_role_name_map`으로 job_name/grade 보정.

**효과**: “테이블에 아이템이 없어서 None” 같은 상황 제거, 읽기/쓰기 경로 단순화.

---

### 2.3 3단계: 변경 알림 디바운스

**목표**: 입력이 멈춘 뒤 한 번만 노무비 상세·요약·경비입력 반영.

**방법**:
- `_handle_item_changed`에서 `_external_on_change()`를 곧바로 호출하지 말고, **QTimer.singleShot(400ms)** 로 한 번만 예약.
- 400ms 안에 또 `itemChanged`가 오면 이전 타이머는 무시하고 새로 400ms 예약.
- 타이머가 실제로 도는 시점에만 `_external_on_change()` 호출.

**효과**: 타이핑 중에는 무거운 연산을 하지 않아, 에러 가능성과 지연이 동시에 줄어듦.

---

### 2.4 4단계: 디버그/훅 조건부 비활성화

**목표**: 프로덕션에서는 테이블 훅/과한 로그가 돌지 않게 함.

**방법**:
- `attach_table_debug_hooks`, `hook_suspicious_methods` 호출을 **환경 변수** (예: `COSTCALC_DEBUG_TABLE=1`) 또는 **로깅 레벨**이 DEBUG일 때만 수행.
- `_force_editable_full` 내부의 `QTimer.singleShot(0/200ms)` 디버그 덤프도 같은 조건에서만 실행.

**효과**: 일상 사용 시 불필요한 로그/타이머가 사라져, 테이블 동작이 단순해짐.

---

## 3. 적용 순서 권장

| 순서 | 항목 | 기대 효과 |
|------|------|-----------|
| 1 | 직무코드 컬럼 Delegate 전환 (2.1) | 직무코드 관련 버그·예외 대부분 제거 |
| 2 | 변경 알림 디바운스 (2.3) | 입력 중 오류·지연 감소 |
| 3 | 디버그 훅 조건부 (2.4) | 동작 단순화 |
| 4 | 내부 모델 (2.2) | 유지보수·확장 시 데이터 경로 명확 |

1단계만 적용해도 “직무코드가 사라짐 / 덮어쓰기 / Enter 키 꼬임” 같은 문제는 크게 줄일 수 있음.  
원하시면 1단계(Delegate 전환)부터 구체적인 패치 포인트(파일·함수·코드 위치)로 쪼개서 적용안을 이어서 작성할 수 있습니다.

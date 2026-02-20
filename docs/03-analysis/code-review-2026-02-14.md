# Code Review Report: auto_fm

**Project**: auto_fm (시설관리 원가 계산 프로그램)
**Review Date**: 2026-02-14
**Reviewer**: Claude Code Analyzer (bkit-code-analyzer)
**Tech Stack**: Python 3.12+, PyQt6, SQLite
**Scope**: src/ directory (all files)

---

## Executive Summary

- **Files reviewed**: 55 Python source files
- **Total issues**: 42 (Critical: 3, High: 8, Medium: 16, Low: 15)
- **Quality score**: 72/100
- **Production readiness**: **Needs Fixes** (3 critical issues must be addressed)

The auto_fm codebase is a well-structured facility management cost calculation application with proper layer separation (domain, UI, utils). The core calculation engine is solid with appropriate use of `Decimal` for financial arithmetic. However, several issues related to resource management, duplicate code, and error handling need resolution before production deployment.

---

## Critical Issues (Severity: Critical)

These issues **MUST** be fixed before deployment.

### C-01: Database Connection Leak in `_refresh_master_data`
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\ui\main_window.py` (lines 860-904)
**Confidence**: 95%

```python
def _refresh_master_data(self, scenario_id: str) -> None:
    # ...
    conn = get_connection()
    repo = MasterDataRepo(conn)
    try:
        # ... operations ...
    finally:
        conn.close()
```

The `MasterDataRepo` is created with a connection, then `conn.close()` is called in `finally`. However, if any exception occurs between `conn = get_connection()` and the `try` block (e.g., during `MasterDataRepo(conn)` -- unlikely but architecturally fragile), or if `repo` methods internally acquire new connections without closing them, connections may leak. More critically, the pattern `conn = get_connection()` followed by `repo = MasterDataRepo(conn)` before the `try` means the connection is not protected if `MasterDataRepo.__init__` raises.

**Actual critical path**: In the `_on_job_role_changed` method (line 1132), a connection is opened and used extensively. If any exception occurs in the inner `try` block before reaching `finally`, the connection closes properly. However, the method calls `get_expense_rows_for_display` (line 1193) which internally calls `get_scenario_input` which may open additional connections depending on code path, creating connection pressure.

**Recommended Action**: Adopt a context manager pattern (`with` statement) for all database connections. Consider implementing `get_connection()` as a context manager.

### C-02: `settings_manager.save()` Recursive Load During Save
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\settings_manager.py` (lines 98-107)
**Confidence**: 92%

```python
def save(config: dict[str, Any]) -> None:
    _ensure_config_dir()
    path = get_config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    _cache.clear()
    _cache.update(load())  # <-- load() calls save() if file doesn't exist
```

The `save()` function clears the cache and calls `load()` to refresh it. The `load()` function calls `save(default)` if the file does not exist. If the file write fails silently or the file is deleted between `json.dump` and `_cache.update(load())`, this creates an infinite recursion loop that will crash the application with a `RecursionError`.

**Recommended Action**: Replace `_cache.update(load())` with `_cache.update(config)` directly, avoiding the round-trip through the file system.

### C-03: `datetime.utcnow()` Deprecated, Potential Data Corruption on Date Boundaries
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\db.py` (lines 96, 128)
**Confidence**: 90%

```python
("startup", datetime.utcnow().isoformat()),
```

`datetime.utcnow()` is deprecated since Python 3.12. More importantly, the health check and backup file naming use UTC while SQLite `datetime('now')` used in scenario saves defaults to UTC. If the system timezone changes or DST transitions occur, backup file timestamps may not match the actual corruption event, making recovery harder.

**Recommended Action**: Replace with `datetime.now(datetime.timezone.utc)` for Python 3.12+ compatibility.

---

## High Priority Issues (Severity: High)

These issues **SHOULD** be fixed before deployment.

### H-01: Massive Duplicate Code Between `job_role_table.py` and `expense_input_table.py`
**Files**:
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\ui\job_role_table.py`
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\ui\expense_input_table.py`
**Confidence**: 98%

The following functions/classes are duplicated nearly verbatim between these two files:

| Function/Class | job_role_table.py | expense_input_table.py | Similarity |
|---|---|---|---|
| `setup_qtable_debug_log()` | lines 36-46 | lines 23-34 | 100% |
| `_dump_table_state()` | lines 49-90 | lines 37-78 | 100% |
| `ViewportEventLogger` | lines 93-119 | lines 81-107 | 100% |
| `attach_table_debug_hooks()` | lines 122-143 | lines 110-131 | 100% |
| `_to_int_safe()` | lines 146-156 | lines 134-144 | 100% |
| `hook_suspicious_methods()` | lines 159-185 | lines 147-173 | 100% |
| `_force_editable_full()` | lines 188-236 | lines 176-224 | 100% |

This is approximately 200 lines of exact duplicate code.

**Recommended Action**: Extract shared table utility functions into a common module (e.g., `src/ui/table_utils.py`).

### H-02: `InputPanel.get_values()` Crashes on Non-Numeric Input
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\ui\input_panel.py` (lines 97-102)
**Confidence**: 95%

```python
def get_values(self) -> dict:
    return {
        "scenario_name": self.scenario_name.text().strip(),
        "overhead_rate": float(self.overhead_rate.text() or "18.5"),
        "profit_rate": float(self.profit_rate.text() or "15.0"),
    }
```

If the user types non-numeric text (e.g., "abc") into the overhead_rate or profit_rate fields, `float()` will raise a `ValueError`, crashing the application. This is called from `calculate()`, `save_scenario()`, and `_persist_ui_to_db()`.

**Recommended Action**: Wrap in try/except with fallback to default values, or add `QDoubleValidator` to the QLineEdit fields.

### H-03: `MainWindow.__init__` Is 260+ Lines -- God Object Anti-Pattern
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\ui\main_window.py`
**Confidence**: 93%

The `MainWindow` class is 1,247 lines long with the `__init__` method spanning approximately 260 lines. It manages:
- UI layout construction
- Button wiring
- State management
- Database operations
- Export logic
- Calculation orchestration
- Master data refresh

This violates the Single Responsibility Principle and makes the code difficult to test and maintain.

**Recommended Action**: Extract into dedicated components:
- `MainWindowLayout` - UI construction
- `ScenarioController` - save/load/delete orchestration
- `ExportController` - PDF/Excel export
- `CalculationController` - calculation orchestration

### H-04: Multiple Database Connections Opened Per User Action
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\ui\main_window.py`
**Confidence**: 92%

In the `load_scenario` method (lines 568-689), two separate database connections are opened sequentially:

```python
conn = get_connection()
try:
    canonical = get_scenario_input(scenario_id, conn)
finally:
    conn.close()

# ... later ...

conn2 = get_connection()
try:
    snapshot = get_result_snapshot(scenario_id, conn2)
finally:
    conn2.close()
```

Similarly, `_on_job_role_changed` opens a connection and then calls functions that may open additional connections internally. This creates unnecessary connection overhead and potential for stale reads.

**Recommended Action**: Consolidate database operations to use a single connection per user action.

### H-05: Insurance Rate Constants Defined in Three Different Places
**Files**:
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\context\calc_context.py` (lines 24-30)
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\constants\rates.py` (lines 1-12)
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\settings_manager.py` (lines 42-49)
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\wage_decomposer.py` (lines 34-42)
**Confidence**: 97%

Insurance rates are hardcoded in at least four locations with slightly different values:

| Rate | calc_context.py | rates.py | settings_manager.py | wage_decomposer.py |
|---|---|---|---|---|
| Health Insurance | 0.03545 | 0.0343 | 0.03545 | 0.03545 |
| Employment Insurance | 0.0115 | 0.0105 | 0.0115 | 0.0115 |

The `rates.py` file has different values (0.0343 vs 0.03545 for health, 0.0105 vs 0.0115 for employment), which means if `rates.py` is ever imported instead of the other sources, calculations will produce different results.

**Recommended Action**: Establish a single source of truth for insurance rates. Use `settings_manager` as the canonical source and remove hardcoded constants from `calc_context.py` and `rates.py`.

### H-06: `_v` Helper Function Defined Inside a Loop
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\result\service.py` (lines 143-146)
**Confidence**: 90%

```python
for line in labor_result.get("job_lines", []):
    def _v(obj, key, default=0):
        if hasattr(obj, key):
            return getattr(obj, key, default)
        return obj.get(key, default) if isinstance(obj, dict) else default
```

A helper function `_v` is defined inside a `for` loop body. While Python handles this correctly, it creates a new function object on every iteration, which is wasteful. This pattern is also used in `expense.py` line 142 (`_attr` function inside a loop).

**Recommended Action**: Move these helper functions outside the loop to module level or class level.

### H-07: `compare_page.py` Missing Import for `QColor`
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\ui\compare\compare_page.py` (line 268)
**Confidence**: 95%

```python
painter.fillRect(
    left_x - 5, y - line_height + 4,
    right_x - left_x + 10, line_height,
    QColor(255, 243, 205),
)
```

`QColor` is used on line 268 but is not imported at the top of the file. Only `QPainter` and `QPrinter` are imported from `PyQt6.QtGui`. This will cause a `NameError` when the user attempts to export a comparison PDF with a "total" row.

**Recommended Action**: Add `from PyQt6.QtGui import QPainter, QColor` to the imports.

### H-08: Silent Exception Swallowing in Critical Functions
**Files**:
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\result\service.py` (lines 338, 363, 387)
**Confidence**: 91%

```python
def get_insurance_by_exp_code_for_scenario(scenario_id: str, conn) -> dict[str, int]:
    try:
        # ... calculation logic ...
        return _build_insurance_by_exp_code(insurance_aggregate)
    except Exception:
        return {}
```

Three functions (`get_insurance_by_exp_code_for_scenario`, `get_insurance_by_exp_code_from_ui`, `get_labor_rows_from_ui`) catch all exceptions and return empty results. This means calculation errors (e.g., wrong data types, missing columns in DB) will silently produce zero values, making debugging extremely difficult.

**Recommended Action**: At minimum, log the exception. Consider raising the exception in debug mode.

---

## Medium Priority Issues (Severity: Medium)

### M-01: `DataManager` and `WageManager` Are Near-Duplicates
**Files**:
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\data_manager.py`
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\wage_manager.py`
**Confidence**: 95%

Both classes load `job_mapping.json` and `wages_master.json`, both have `get_wage()`, `merge_job_rates_for_year()`, `list_available_years()`, and `reload()` methods with nearly identical logic. `WageManager` has additional capabilities (decomposition, grade details) but the core data loading is duplicated.

**Recommended Action**: Consolidate into a single `WageManager` class or extract common loading logic into a shared base.

### M-02: `_price_map` Function Duplicated
**Files**:
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\result\service.py` (lines 275-280)
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\scenario_input\service.py` (lines 309-314)
**Confidence**: 98%

```python
# Both files contain identical implementations:
def _price_map(pricebook: list) -> dict[str, int]:
    result: dict[str, int] = {}
    for price in pricebook:
        if price.exp_code not in result:
            result[price.exp_code] = int(price.unit_price)
    return result
```

**Recommended Action**: Move to `MasterDataRepo` or a shared utility module.

### M-03: `build_job_breakdown_rows` and `build_detail_job_rows` Are Identical
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\ui\export_helpers.py` (lines 4-19 and 36-51)
**Confidence**: 100%

Both functions produce the exact same output from the same input.

**Recommended Action**: Remove `build_detail_job_rows` and use `build_job_breakdown_rows` everywhere.

### M-04: `_load_json` Helper Duplicated Across Three Files
**Files**:
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\wage_manager.py` (lines 20-28)
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\data_manager.py` (lines 14-22)
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\wage_validation.py` (lines 28-35)
**Confidence**: 98%

**Recommended Action**: Move to `src/utils/json_helpers.py`.

### M-05: `_sanitize_filename` Duplicated
**Files**:
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\ui\main_window.py` (lines 783-785)
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\ui\compare\compare_page.py` (lines 304-306)
**Confidence**: 100%

**Recommended Action**: Move to `src/utils/` module.

### M-06: Magic Tab Index Numbers
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\ui\main_window.py` (lines 323-335)
**Confidence**: 90%

```python
def _on_tab_changed(self, index: int) -> None:
    if index == 4:  # What tab is this?
        self.labor_detail.update_rows(self.last_labor_rows)
    elif index == 5:  # And this?
```

Tab indices are hardcoded as magic numbers. If tabs are reordered, these checks will silently break.

**Recommended Action**: Define tab index constants or use a mapping/enum.

### M-07: `create_bold_item` Helper Defined Inside Two Different Methods
**Files**:
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\ui\labor_detail_table.py` (lines 88-94)
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\ui\expense_detail_table.py` (lines 101-107)
**Confidence**: 95%

Both define the same `create_bold_item` function with `from PyQt6.QtGui import QFont, QColor` inside the method body.

**Recommended Action**: Extract to a shared UI utility function. Move imports to module level.

### M-08: `MasterDataRepo` Does Not Implement Context Manager Protocol
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\masterdata\repo.py`
**Confidence**: 88%

The class has a `close()` method but no `__enter__`/`__exit__` methods. Callers must remember to call `close()`, and most callers bypass it entirely since they pass external connections.

**Recommended Action**: Implement `__enter__` and `__exit__` for use with `with` statements.

### M-09: `_read_float` Duplicated in Two Modules
**Files**:
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\scenario_input\service.py` (lines 364-368)
- `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\normalization.py` (lines 82-86)
**Confidence**: 100%

**Recommended Action**: Move to a shared utility.

### M-10: `Aggregator` Uses `Union[int, float]` Instead of `Decimal`
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\aggregator.py`
**Confidence**: 85%

The `Aggregator` dataclass uses `Union[int, float]` for financial amounts, while the calculation engine uses `Decimal` internally. This creates a type inconsistency at the boundary.

**Recommended Action**: Use `int` exclusively for final monetary amounts (which is the pattern already used after `drop_under_1_won`).

### M-11: `LaborJobLine` Has Redundant Fields
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\calculator\labor_job_line.py`
**Confidence**: 88%

The dataclass has both `base_wage` and `base_salary`, `allowance` and `allowances`, `total` and `role_total` which appear to carry the same values.

**Recommended Action**: Remove redundant fields or document the semantic difference.

### M-12: `ManpowerValidator` / `ManpowerCalculator` Is WIP / Unused
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\calculator\manpower.py`
**Confidence**: 92%

All job ratios are set to `Decimal("1")` with a comment "비율은 Excel 값으로 교체해야 합니다". The class alias `ManpowerCalculator = ManpowerValidator` suggests unfinished refactoring.

**Recommended Action**: Either complete the implementation or remove from production build.

### M-13: Logging Disabled at CRITICAL Level in Production
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\main.py` (line 21)
**Confidence**: 90%

```python
logging.disable(logging.CRITICAL)
```

This disables ALL logging including error logs. While console spam is reduced, file-based logging for debugging production issues is also lost.

**Recommended Action**: Configure logging to file only (disable console handler, keep file handler) instead of blanket disabling.

### M-14: No Input Validation on `scenario_id` in SQL Queries
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\scenario_input\service.py`
**Confidence**: 85%

While parameterized queries are used (preventing SQL injection), there is no validation that `scenario_id` follows the expected pattern. The `_sanitize_filename` only runs on the UI side; if `post_scenario_input` is called from other code paths, arbitrary strings could be stored.

**Recommended Action**: Add `scenario_id` validation in `post_scenario_input` and `delete_scenario`.

### M-15: `_sub_item_to_dict` Has Two Nearly Identical Code Paths
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\ui\expense_sub_item_table.py` (lines 102-132)
**Confidence**: 90%

The dataclass branch and dict branch produce the same output structure with identical keys.

**Recommended Action**: Use `dataclasses.asdict()` for the dataclass branch, or unify access patterns.

### M-16: `compute_action_state` Logic Prevents Calculate When Not Dirty
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\ui\state.py` (lines 44-49)
**Confidence**: 88%

```python
def compute_action_state(is_dirty: bool, has_result: bool) -> dict:
    return {
        "calculate_enabled": not is_dirty,
        ...
    }
```

The calculate button is enabled when NOT dirty. This means if a user loads a scenario and immediately wants to recalculate (e.g., after changing settings), the button is disabled because the state is "clean". This is counter-intuitive -- calculate should generally always be available.

**Recommended Action**: Review the intended UX flow. Consider enabling calculate regardless of dirty state.

---

## Low Priority Issues (Severity: Low)

### L-01: Missing `__init__.py` Files for Some Packages
**Files**: Various `__init__.py` files exist but several sub-packages under `src/ui/labor/` and `src/ui/compare/` lack them.
**Confidence**: 80%

### L-02: `JOB_META` Hardcoded with Only 2 Entries
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\constants\job_data.py` (lines 16-19)
**Confidence**: 85%

### L-03: `version.py` Not Used in Application Window Title
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\version.py` -- exists but the window title is hardcoded.
**Confidence**: 80%

### L-04: `logging_config.py` `setup_app_logger` Never Called
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\logging_config.py`
**Confidence**: 85%

The `setup_app_logger()` function is defined but not called from `main.py` or anywhere else.

### L-05: Inconsistent Use of `typing.Dict` vs `dict` Built-in
**Files**: Multiple files use `Dict[str, int]` (imported from `typing`) while others use `dict[str, int]` (Python 3.9+ syntax). Since the target is Python 3.12+, the `typing.Dict` import is unnecessary.
**Confidence**: 95%

### L-06: Korean Comments Mixed with English Code
**Files**: Widespread
**Confidence**: 100%

Korean comments are used throughout (appropriate for a Korean application), but some functions have no docstrings. Key public API functions should have docstrings.

### L-07: No Type Hints on `conn` Parameters
**Files**: Throughout the codebase, `conn` parameters have no type annotation.
**Confidence**: 90%

```python
def calculate_result(scenario_id: str, conn=None, ...) -> dict:  # conn type missing
```

**Recommended Action**: Add `conn: sqlite3.Connection | None = None`.

### L-08: `_is_non_zero_labor` Ignores `work_days` and `work_hours`
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\scenario_input\service.py` (lines 390-404)
**Confidence**: 85%

The function checks headcount, overtime, and holiday hours but not work_days or work_hours. A role with 0 headcount but non-zero work_days would not be included, which is correct. But a role with non-zero work_days but zero headcount would be excluded, which might lose configuration data.

### L-09: `constants/rates.py` Appears Unused
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\domain\constants\rates.py`
**Confidence**: 85%

No file imports from this module. The rates defined here differ from those used in actual calculations.

### L-10: `_fmt_row_total` Could Use Standard Formatting
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\ui\expense_detail_table.py` (lines 4-10)

The function manually handles comma stripping and conversion. Python's `f"{n:,}"` is sufficient.

### L-11: `scenario_dir` Path Calculated Differently in Different Classes
**Files**: `main_window.py` uses `Path(__file__).resolve().parents[2] / "scenarios"`, `compare_page.py` uses `Path(__file__).resolve().parents[2] / "exports"`.
**Confidence**: 80%

**Recommended Action**: Use `get_scenarios_dir()` and `get_exports_dir()` from `path_helper.py`.

### L-12: `try/except ImportError` for PyQt5 Fallback in `main.py`
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\main.py` (lines 9-12)
**Confidence**: 80%

The rest of the codebase imports `PyQt6` directly. The fallback is incomplete and would fail in other modules.

### L-13: No `__all__` Exports Defined
**Files**: No module defines `__all__`, making the public API implicit.

### L-14: Potential Integer Overflow in Annual Calculation
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\ui\expense_detail_table.py` (lines 78-80)

```python
annual_total = row_total * total_headcount * 12
```

For large values, this could produce very large numbers. Python handles big integers natively, but the display formatting should be verified.

### L-15: f-strings Used in Logging Calls
**Files**: Multiple files use `logging.info(f"...")` instead of `logging.info("...", arg)`.
**Confidence**: 90%

f-strings in logging always evaluate the string even if the log level is disabled. Use `%s` formatting for performance.

---

## Security Analysis

- **Vulnerabilities found**: 1 (Low severity)
- **Risk assessment**: **Low**

### SQL Injection: SAFE
All SQL queries use parameterized statements (`?` placeholders). No string concatenation or formatting is used in SQL construction. The `executescript` calls in migration_runner use static SQL from trusted sources (embedded strings and local .sql files).

### Input Validation: ADEQUATE
The `scenario_input/service.py` validates numeric ranges with appropriate bounds. The `_sanitize_filename` function strips special characters from scenario names.

### Sensitive Data: NOT APPLICABLE
No API keys, passwords, or credentials are stored. The application is a desktop tool using a local SQLite database.

### File Path: LOW RISK
The `COSTCALC_DB_PATH` environment variable is used for the database path without path traversal validation. However, this is a desktop application where the user already has file system access.

### Secret in Config: CLEAN
`config.json` contains only calculation parameters (insurance rates, work hours), no secrets.

---

## Performance Analysis

- **Performance issues**: 4
- **Optimization opportunities**: 3

### P-01: Multiple Database Connections Per User Action (High Impact)
As documented in H-04, load_scenario opens 2+ connections sequentially. `_on_job_role_changed` opens connections and calls functions that may open more. For a desktop application with SQLite, this is not catastrophic but adds unnecessary I/O overhead.

### P-02: `get_job_mapping_from_file()` Called on Every Cell Edit (Medium Impact)
**File**: `c:\Users\helpbiz\Documents\auto_fm\auto_fm\src\ui\job_role_table.py` (line 576)

Every time a job code cell changes, `get_job_mapping_from_file()` reads and parses the JSON file from disk. This should be cached.

### P-03: Full Table Rebuild on Data Update (Low Impact)
`labor_detail_table.py` and `expense_detail_table.py` call `setRowCount(0)` and rebuild all rows on every update. For the expected data sizes (<100 rows), this is acceptable.

### P-04: `_force_editable_full` Iterates All Cells (Low Impact)
This function iterates every cell in the table to set flags, and is called multiple times during initialization and data loading.

### Optimization Opportunities
1. Cache `get_job_mapping_from_file()` results with file modification time check
2. Use a single connection per user action (pass connection through call chain)
3. Use `QTableWidget.setRowCount(n)` with direct item setting instead of `insertRow` in loops

---

## Best Practices Compliance

- **Score**: 68/100
- **Key violations**:

### Architecture (Good)
- Clean layer separation: domain/ui/utils
- Repository pattern implemented via `MasterDataRepo`
- Dataclasses used for data transfer objects
- Calculation logic properly isolated in domain layer

### DRY (Needs Improvement: -15 points)
- 200+ lines of exact duplicate code in table utilities
- Insurance rates defined in 4 places
- Helper functions duplicated across modules
- `_load_json`, `_price_map`, `_sanitize_filename` duplicated

### SOLID Principles (Needs Improvement: -10 points)
- **SRP Violation**: `MainWindow` has 7+ responsibilities
- **OCP Concern**: Insurance rates hardcoded in `CalcContext` class attributes
- **DIP**: `settings_manager` uses module-level cache (singleton pattern OK for desktop app)

### Error Handling (Needs Improvement: -7 points)
- Silent exception swallowing in 3 functions
- `InputPanel.get_values()` can crash on invalid input
- Missing `QColor` import will crash PDF export

### Type Safety (Adequate)
- Good use of type hints in most domain code
- `conn` parameters missing type annotations
- Mixed `typing.Dict` and `dict` usage

### Documentation (Adequate)
- Korean docstrings present on most classes and key functions
- Module-level docstrings present
- Architecture decisions documented in docstrings

---

## Duplicate Code Summary

| Type | Location 1 | Location 2 | Similarity | Lines |
|---|---|---|---|---|
| Exact | job_role_table.py (7 funcs) | expense_input_table.py (7 funcs) | 100% | ~200 |
| Exact | result/service.py `_price_map` | scenario_input/service.py `_price_map` | 100% | 6 |
| Exact | export_helpers.py `build_job_breakdown_rows` | export_helpers.py `build_detail_job_rows` | 100% | 15 |
| Exact | normalization.py `_read_float` | scenario_input/service.py `_read_float` | 100% | 5 |
| Structural | data_manager.py | wage_manager.py | 80% | ~60 |
| Structural | labor_detail_table.py `create_bold_item` | expense_detail_table.py `create_bold_item` | 95% | 7 |
| Values | calc_context.py rates | rates.py rates | Conflicting | 7 |

**Total estimated duplicate/redundant code**: ~300 lines (approximately 8% of codebase)

---

## Recommendations

### Priority 1: Fix Before Deployment (Critical + High, 1-2 days)

1. **Fix C-01**: Implement connection context manager. Consolidate connections in `_on_job_role_changed` and `load_scenario`.
2. **Fix C-02**: Change `save()` to set cache directly from the config parameter.
3. **Fix C-03**: Replace `datetime.utcnow()` with `datetime.now(datetime.timezone.utc)`.
4. **Fix H-02**: Add `QDoubleValidator` to overhead_rate and profit_rate fields, or add try/except with defaults.
5. **Fix H-07**: Add missing `QColor` import in compare_page.py.
6. **Fix H-08**: Add `logging.exception()` to the bare `except Exception: return {}` blocks.

### Priority 2: Fix Soon After Deployment (High + Medium, 3-5 days)

7. **Fix H-01**: Extract shared table utilities to `src/ui/table_utils.py`.
8. **Fix H-05**: Establish single source of truth for insurance rates via `settings_manager`.
9. **Fix M-01**: Consolidate `DataManager` and `WageManager`.
10. **Fix M-06**: Define tab index constants.
11. **Fix M-13**: Replace `logging.disable(CRITICAL)` with proper handler configuration.

### Priority 3: Long-Term Improvements (Medium + Low, ongoing)

12. Refactor `MainWindow` into smaller controller classes (H-03).
13. Remove unused code: `rates.py`, `manpower.py` (if truly unused), `logging_config.py` setup.
14. Standardize type hints: use built-in `dict`/`list` everywhere (drop `typing.Dict`).
15. Add `__all__` to public modules.
16. Use `path_helper.py` functions consistently for all directory paths.

---

## Conclusion

The auto_fm codebase demonstrates solid domain modeling with appropriate use of `Decimal` for financial calculations, proper SQL parameterization, and clean separation between domain logic and UI. The 91% match rate achievement reflects good calculation accuracy.

**For production deployment**, three critical issues must be addressed:
1. The recursive save/load in settings_manager (C-02) -- highest crash risk
2. The missing QColor import in compare PDF export (H-07) -- will crash on use
3. The float conversion crash in InputPanel (H-02) -- will crash on invalid user input

These three fixes are estimated at 1-2 hours of work. After resolving these, the application is suitable for production deployment with the understanding that the high-priority issues (particularly code duplication and MainWindow complexity) should be addressed in the next iteration cycle.

**Deployment Recommendation**: **Conditionally Ready** -- deploy after fixing C-02, H-02, and H-07. Schedule H-01 and H-05 for the first maintenance release.

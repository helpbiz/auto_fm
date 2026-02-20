# Refactoring Plan: 4-Step Workflow

## Old → New Location Checklist

### (1) Scenario name / creation
| Old | New |
|-----|-----|
| `src/ui/input_panel.py` (scenario_name field, scenario list) | `app/ui/input_panel.py` (unchanged widget), scenario name in `ScenarioContext` |
| `src/ui/main_window.py` `last_scenario_id`, `last_scenario_name`, `_sanitize_filename` | `app/controllers/context.py` `ScenarioContext` |
| `src/domain/scenario_input/service.py` `list_scenario_ids`, `get_scenario_input` | `app/repositories/scenario_repository.py` |

### (2) Base data input (NO calculations)
| Old | New |
|-----|-----|
| `src/ui/state.py` `build_canonical_input` | `app/domain/models.py` `BaseData` from dict; UI still builds dict → service converts |
| `src/ui/job_role_table.py` `get_job_inputs()` | UI collects → controller passes to service/repo |
| `src/ui/expense_sub_item_table.py` `get_all_sub_items()` | UI collects → controller passes |
| `src/ui/input_panel.py` `get_values()` | UI collects scenario_name + base year |
| Raw dicts from UI | `app/domain/models.py` `BaseData`, `LaborInput`, `ExpenseInput` |

### (3) Aggregation (PURE computation)
| Old | New |
|-----|-----|
| `src/domain/result/service.py` `calculate_result(scenario_id, conn)` | `app/services/aggregate_service.py` `aggregate(scenario_id, conn)` → loads base_data + master, calls **same** `_calculate_labor` / `_calculate_expenses` (no change to formulas) |
| `src/domain/result/service.py` `_calculate_labor`, `_calculate_expenses`, `_build_insurance_by_exp_code` | Keep in `src/domain/result/service.py`; AggregateService imports and uses them with in-memory data |
| `src/domain/aggregator.py` `Aggregator` | Unchanged; result wrapped in `ResultSnapshot` dataclass |
| Result dict `labor_rows`, `expense_rows`, `aggregator` | `app/domain/models.py` `ResultSnapshot` |

### (4) Save / load / export
| Old | New |
|-----|-----|
| `src/domain/scenario_input/service.py` `post_scenario_input`, `get_scenario_input`, `delete_scenario` | `app/repositories/scenario_repository.py` (wrap same logic) |
| `src/domain/result/service.py` `_save_result_snapshot`, `get_result_snapshot` | `app/repositories/result_repository.py` or same scenario_repo |
| `src/ui/main_window.py` `_persist_ui_to_db`, `save_scenario`, `load_scenario` | `app/controllers/save_controller.py`, `load_controller.py`; **Save blocked if no snapshot** |
| `src/domain/masterdata/repo.py` `MasterDataRepo` | Used by repositories; no move, call from `app/repositories` |
| Export PDF/Excel | `app/controllers/export_controller.py` or keep in main_window calling repo for snapshot |

### Guards & flow
| Old | New |
|-----|-----|
| `job_role_table.dirty`, `expense_sub_item_table.dirty` | Keep; add `ScenarioContext.is_loading` / `is_dirty`; during load: block signals, no aggregate |
| `_on_job_role_changed` (auto recalc) | Optional: keep for “live” labor detail only, or remove; **never** auto-run full aggregate |
| 집계 실행 button | `AggregateController.run()` → persist base_data → `AggregateService.aggregate()` → store snapshot in context → update UI |
| 시나리오 저장 button | `SaveController.save()` → **guard: no snapshot → message box** → `ScenarioRepository.save()` |

### Dependency direction
- `app/ui` → `app/controllers` only (no direct service/repo in UI).
- `app/controllers` → `app/services`, `app/repositories`, `app/domain`.
- `app/services` → `app/domain`, `src.domain` (calculator/result) only.
- `app/repositories` → `app/domain`, `src.domain.db`, `src.domain.scenario_input`, `src.domain.masterdata.repo`.

---

## Implementation commits (logical chunks)

1. **Commit 1**: Add `app/domain/models.py`, `app/controllers/context.py`, `app/services/aggregate_service.py` (skeleton), `app/repositories/scenario_repository.py` (skeleton), `app/main.py` that launches existing `MainWindow` (no behavior change).
2. **Commit 2**: Move aggregate logic into `AggregateService.aggregate()` by calling existing `calculate_result` or internal `_calculate_labor`/`_calculate_expenses` with data loaded in service; return `ResultSnapshot`.
3. **Commit 3**: Wire “집계 실행” to `AggregateController.run()`, add loading/dirty guards, “시나리오 저장” to `SaveController.save()` with snapshot check.
4. **Commit 4**: Migrate save/load to use `ScenarioRepository`; enforce “Save blocked unless snapshot exists”; optional `ResultRepository` for snapshot.
5. **Commit 5**: Cleanup dead code, add unit test for aggregate with small fixture, run smoke test.

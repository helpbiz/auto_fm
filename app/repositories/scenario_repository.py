"""
Persistence: scenario input, master data refs, and result snapshot.
Wraps src.domain.scenario_input and result storage. No UI.
"""
import json
import logging
from decimal import Decimal
from typing import Any

from app.domain.models import ResultSnapshot
from src.domain.db import get_connection
from src.domain.scenario_input.service import (
    get_scenario_input,
    list_scenario_ids,
    post_scenario_input,
    delete_scenario as delete_scenario_data,
)


class ScenarioRepository:
    """Load/save scenario and snapshot. No calculation logic."""

    def list_ids(self) -> list[str]:
        conn = get_connection()
        try:
            return list_scenario_ids(conn)
        finally:
            conn.close()

    def get_canonical(self, scenario_id: str) -> dict:
        conn = get_connection()
        try:
            return get_scenario_input(scenario_id, conn)
        finally:
            conn.close()

    def save_base_data(self, scenario_id: str, canonical: dict) -> None:
        """Persist scenario input only (no snapshot)."""
        conn = get_connection()
        try:
            post_scenario_input(canonical, scenario_id, conn)
            logging.info("시나리오 저장소: 기본 데이터 저장 완료 시나리오=%s", scenario_id)
        finally:
            conn.close()

    def save_snapshot(self, scenario_id: str, snapshot: ResultSnapshot) -> None:
        """Persist result snapshot to calculation_result table."""
        conn = get_connection()
        try:
            payload = snapshot.to_dict()
            def _json_default(obj: Any) -> Any:
                if isinstance(obj, Decimal):
                    return float(obj)
                raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
            json_str = json.dumps(payload, ensure_ascii=True, default=_json_default)
            conn.execute(
                """
                INSERT INTO calculation_result (scenario_id, result_json, updated_at)
                VALUES (?, ?, datetime('now'))
                ON CONFLICT(scenario_id) DO UPDATE SET
                  result_json=excluded.result_json,
                  updated_at=datetime('now')
                """,
                (scenario_id, json_str),
            )
            conn.commit()
            logging.info("시나리오 저장소: 집계 스냅샷 저장 완료 시나리오=%s", scenario_id)
        finally:
            conn.close()

    def save_scenario_with_snapshot(
        self,
        scenario_id: str,
        scenario_name: str,
        result_snapshot: ResultSnapshot | None,
    ) -> None:
        """
        Ensure snapshot is stored. Base data is expected to be already persisted by caller.
        (Snapshot is usually stored during aggregate; this is a no-op or overwrite.)
        """
        if result_snapshot is not None:
            self.save_snapshot(scenario_id, result_snapshot)

    def delete(self, scenario_id: str) -> None:
        conn = get_connection()
        try:
            delete_scenario_data(scenario_id, conn)
        finally:
            conn.close()

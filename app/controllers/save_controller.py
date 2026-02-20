"""
Step 4: Save scenario + snapshot. Blocked unless result snapshot exists.
"""
import logging
from typing import Callable

from app.controllers.context import ScenarioContext
from app.repositories.scenario_repository import ScenarioRepository


class SaveController:
    """Save is blocked unless an aggregate result snapshot exists."""

    def __init__(
        self,
        context: ScenarioContext,
        scenario_repository: ScenarioRepository,
    ) -> None:
        self._ctx = context
        self._repo = scenario_repository

    def can_save(self) -> bool:
        """Save allowed only when we have a snapshot (aggregate was run)."""
        return self._ctx.has_snapshot() and bool(self._ctx.scenario_id)

    def save(
        self,
        scenario_id: str,
        scenario_name: str,
        persist_base_data: Callable[[], bool],
        on_success: Callable[[], None],
        on_error: Callable[[str], None],
        on_blocked: Callable[[str], None],
    ) -> None:
        """
        Persist scenario (base data + snapshot). If no snapshot, call on_blocked and return.
        """
        if not scenario_id:
            on_error("시나리오명을 입력하세요.")
            return
        if not self._ctx.has_snapshot():
            logging.warning("저장 컨트롤러: 스냅샷 없음으로 저장 불가")
            on_blocked("저장하려면 먼저 '집계 실행'을 실행하세요.")
            return
        if not persist_base_data():
            on_error("입력 데이터 저장에 실패했습니다.")
            return

        try:
            self._repo.save_scenario_with_snapshot(
                scenario_id,
                scenario_name,
                self._ctx.result_snapshot,
            )
            self._ctx.set_scenario(scenario_id, scenario_name)
            self._ctx.set_dirty(False)
            on_success()
            logging.info("저장 컨트롤러: 저장 완료 시나리오=%s", scenario_id)
        except Exception as e:
            logging.exception("저장 컨트롤러: 저장 실패")
            on_error(str(e))

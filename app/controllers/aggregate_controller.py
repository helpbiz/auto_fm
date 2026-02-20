"""
Step 3: Aggregate execution. Orchestrates persist base_data -> aggregate -> store snapshot -> UI update.
"""
import logging
from typing import Callable

from app.domain.models import BaseData, ResultSnapshot
from app.controllers.context import ScenarioContext
from app.services.aggregate_service import AggregateService


class AggregateController:
    """Run aggregate only after base data is persisted. No auto-run during edit."""

    def __init__(
        self,
        context: ScenarioContext,
        aggregate_service: AggregateService,
    ) -> None:
        self._ctx = context
        self._service = aggregate_service

    def run(
        self,
        scenario_id: str,
        scenario_name: str,
        persist_base_data: Callable[[], bool],
        on_success: Callable[[ResultSnapshot], None],
        on_error: Callable[[str], None],
    ) -> None:
        """
        Execute step 3: persist base data, then run pure aggregate, store snapshot, call on_success.
        persist_base_data() must return True if save succeeded.
        """
        if self._ctx.is_loading:
            logging.warning("집계 컨트롤러: 로딩 중이라 생략")
            on_error("편집 중에는 집계할 수 없습니다.")
            return
        if not scenario_id:
            on_error("시나리오명을 입력하세요.")
            return

        if not persist_base_data():
            on_error("입력 데이터 저장에 실패했습니다.")
            return

        self._ctx.set_scenario(scenario_id, scenario_name)
        self._ctx.set_dirty(False)
        self._ctx.set_loading(True)
        try:
            snapshot = self._service.aggregate(scenario_id)
            if snapshot is None:
                on_error("집계 결과를 생성할 수 없습니다.")
                return
            self._ctx.set_result_snapshot(snapshot)
            on_success(snapshot)
            logging.info("집계 컨트롤러: 집계 완료 시나리오=%s", scenario_id)
        except Exception as e:
            logging.exception("집계 컨트롤러: 집계 실패")
            on_error(str(e))
        finally:
            self._ctx.set_loading(False)

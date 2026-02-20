"""
Scenario context: current scenario id/name, base data, and result snapshot.
Held by controllers; UI never holds this directly.
"""
import logging
from typing import Callable

from app.domain.models import Scenario, BaseData, ResultSnapshot


class ScenarioContext:
    """Singleton-ish: one current scenario per app. Step transitions tracked here."""

    _instance: "ScenarioContext | None" = None

    def __init__(self) -> None:
        self.scenario_id: str = ""
        self.scenario_name: str = ""
        self.base_data: BaseData | None = None
        self.result_snapshot: ResultSnapshot | None = None
        self.is_loading: bool = False
        self.is_dirty: bool = False
        self._listeners: list[Callable[[], None]] = []

    @classmethod
    def get(cls) -> "ScenarioContext":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_scenario(self, scenario_id: str, scenario_name: str) -> None:
        self.scenario_id = scenario_id
        self.scenario_name = scenario_name
        self._notify()

    def set_base_data(self, data: BaseData) -> None:
        self.base_data = data
        self.is_dirty = True
        self._notify()

    def set_result_snapshot(self, snapshot: ResultSnapshot | None) -> None:
        self.result_snapshot = snapshot
        logging.info("시나리오 컨텍스트: 결과 스냅샷 %s", "설정됨" if snapshot else "해제됨")
        self._notify()

    def has_snapshot(self) -> bool:
        return self.result_snapshot is not None

    def set_loading(self, value: bool) -> None:
        self.is_loading = value
        logging.debug("ScenarioContext: is_loading=%s", value)

    def set_dirty(self, value: bool) -> None:
        self.is_dirty = value
        self._notify()

    def clear_after_load(self) -> None:
        """Clear snapshot when switching scenario without aggregate."""
        self.result_snapshot = None
        self._notify()

    def subscribe(self, callback: Callable[[], None]) -> None:
        self._listeners.append(callback)

    def _notify(self) -> None:
        for cb in self._listeners:
            try:
                cb()
            except Exception as e:
                logging.warning("시나리오 컨텍스트 알림 오류: %s", e)

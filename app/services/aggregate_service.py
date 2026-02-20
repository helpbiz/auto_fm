"""
Step 3: Pure aggregation. Delegates to existing calculation logic; no formula changes.
Input: scenario_id (data loaded from DB by this service).
Output: ResultSnapshot.
"""
import logging

from app.domain.models import ResultSnapshot
from src.domain.db import get_connection
from src.domain.result.service import calculate_result


class AggregateService:
    """
    Runs aggregate for a scenario. Loads base data + master from DB, runs existing
    calculate_result (unchanged formulas), returns ResultSnapshot.
    """

    def aggregate(self, scenario_id: str) -> ResultSnapshot | None:
        """
        Execute aggregation for the given scenario_id.
        Reads scenario input and master data from DB; returns result snapshot.
        """
        conn = get_connection()
        try:
            result = calculate_result(scenario_id, conn)
            if not result:
                return None
            snapshot = ResultSnapshot.from_result_dict(result)
            logging.info("집계 서비스: 결과 스냅샷 생성 완료 시나리오=%s", scenario_id)
            return snapshot
        except Exception as e:
            logging.exception("집계 서비스 집계 실패: %s", e)
            raise
        finally:
            conn.close()

from decimal import Decimal
from typing import Dict

from src.domain.constants.rounding import round_up


# NOTE: 아래 비율은 Excel 값으로 교체해야 합니다.
# 임시로 동일 비율을 사용합니다.
JOB_RATIOS: Dict[str, Decimal] = {
    "master": Decimal("1"),
    "professional_engineer": Decimal("1"),
    "special_engineer": Decimal("1"),
    "high_engineer": Decimal("1"),
    "advanced_engineer": Decimal("1"),
    "intermediate_engineer": Decimal("1"),
    "junior_engineer": Decimal("1"),
    "senior_engineer": Decimal("1"),
    "simple_worker": Decimal("1"),
}


class ManpowerValidator:
    """
    인원 산정 검증용 클래스 (WIP)
    """

    def __init__(self, total_households: Decimal, stations: int):
        self.total_households = total_households
        self.stations = Decimal(str(stations))

    def calculate(self) -> Dict[str, Decimal]:
        """
        자동 인원 산정:
        - 2,159 가구당 1인
        - 정거장당 4.82인
        - 둘 중 큰 값을 선택
        - 직무 비율로 분배
        - 올림(ROUND_UP) 적용
        """
        by_households = Decimal(
            round_up(self.total_households / Decimal("2159"))
        )
        by_stations = Decimal(
            round_up(self.stations * Decimal("4.82"))
        )

        total_required = max(by_households, by_stations)

        ratios = self._normalized_ratios()
        result: Dict[str, Decimal] = {}
        for job, ratio in ratios.items():
            count = Decimal(round_up(total_required * ratio))
            result[job] = count

        return result

    def _normalized_ratios(self) -> Dict[str, Decimal]:
        total = sum(JOB_RATIOS.values())
        if total == 0:
            return {job: Decimal("0") for job in JOB_RATIOS}
        return {job: (ratio / total) for job, ratio in JOB_RATIOS.items()}

ManpowerCalculator = ManpowerValidator

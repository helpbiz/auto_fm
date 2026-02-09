from decimal import Decimal, ROUND_HALF_UP, ROUND_FLOOR, ROUND_CEILING
from typing import Union

Number = Union[int, float, Decimal]


def drop_under_1_won(amount: Number) -> int:
    """1원 미만 버림 (정수 원 단위로 내림)."""
    return int(Decimal(str(amount)).to_integral_value(rounding=ROUND_FLOOR))


def drop_under_1000_won(amount: Number) -> int:
    """1,000원 미만 버림 (천원 단위로 내림)."""
    amount_decimal = Decimal(str(amount))
    thousands = (amount_decimal // Decimal("1000")) * Decimal("1000")
    return int(thousands)


def round_half_up(amount: Number, unit: int = 1) -> int:
    """반올림 함수 (unit 단위로 반올림)."""
    if unit <= 0:
        raise ValueError("unit must be a positive integer.")

    amount_decimal = Decimal(str(amount))
    unit_decimal = Decimal(str(unit))
    divided = amount_decimal / unit_decimal
    rounded = divided.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(rounded * unit_decimal)


def round_up(amount: Number, unit: int = 1) -> int:
    """올림 함수 (unit 단위로 올림)."""
    if unit <= 0:
        raise ValueError("unit must be a positive integer.")

    amount_decimal = Decimal(str(amount))
    unit_decimal = Decimal(str(unit))
    divided = amount_decimal / unit_decimal
    rounded = divided.quantize(Decimal("1"), rounding=ROUND_CEILING)
    return int(rounded * unit_decimal)

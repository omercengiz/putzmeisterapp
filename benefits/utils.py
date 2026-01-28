# benefits/utils.py
import math
from decimal import Decimal, InvalidOperation
import datetime


def parse_tr_decimal(value):
    """
    Türk Lirası formatını parse eder:
    10.000,32 -> 10000.32
    1.250 -> 1250
    boş / NaN -> 0
    """
    if value is None:
        return Decimal("0")

    if isinstance(value, float) and math.isnan(value):
        return Decimal("0")

    try:
        s = str(value).strip()
        s = s.replace(".", "")   # binlik
        s = s.replace(",", ".")  # ondalık
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return Decimal("0")


def is_after_exit(year: int, month: int, exit_date: datetime.date) -> bool:
    return (year, month) > (exit_date.year, exit_date.month)
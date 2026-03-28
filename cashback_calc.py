"""Расчёт кэшбэка по правилам карты — общая логика для транзакций, импорта и демо."""
from models import Card


def calculate_cashback(card: Card, category: str, amount: float) -> float:
    cashback_rules = card.cashback_rules or {}
    cashback_percentage = cashback_rules.get(category, cashback_rules.get("прочее", 0))
    if cashback_percentage == 0:
        return 0.0
    return (amount * cashback_percentage) / 100.0

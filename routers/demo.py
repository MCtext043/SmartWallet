"""Демо-наполнение для презентаций: карты и история трат без банковской интеграции."""
from datetime import datetime, timedelta
from typing import List, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from auth import get_current_user
from cashback_calc import calculate_cashback
from database import get_db
from models import Card, Recommendation, Transaction, User
from schemas import DemoSeedResponse

router = APIRouter(prefix="/demo", tags=["demo"])

# Реалистичный набор для питча (условные банки и проценты)
DEMO_CARDS: List[dict] = [
    {
        "bank_name": "Т-Банк",
        "card_name": "Black",
        "last4": "4242",
        "cashback_rules": {"еда": 5, "транспорт": 10, "прочее": 1},
        "limit_monthly": 5000.0,
    },
    {
        "bank_name": "СберБанк",
        "card_name": "СберКарта",
        "last4": "8811",
        "cashback_rules": {"еда": 3, "транспорт": 3, "прочее": 4},
        "limit_monthly": 3000.0,
    },
    {
        "bank_name": "Альфа-Банк",
        "card_name": "Cashback",
        "last4": "1199",
        "cashback_rules": {"еда": 2, "транспорт": 5, "прочее": 6},
        "limit_monthly": 8000.0,
    },
]

# (дней назад, сумма, категория, last4 карты)
DEMO_TXN_SPEC: List[Tuple[int, float, str, str]] = [
    (0, 890.0, "еда", "4242"),
    (0, 2100.0, "транспорт", "8811"),
    (1, 450.0, "еда", "8811"),
    (2, 3200.0, "прочее", "1199"),
    (3, 1200.0, "еда", "1199"),
    (4, 550.0, "транспорт", "4242"),
    (5, 780.0, "еда", "4242"),
    (7, 4100.0, "прочее", "8811"),
    (9, 650.0, "транспорт", "1199"),
    (12, 2340.0, "еда", "8811"),
    (14, 990.0, "прочее", "4242"),
    (18, 1750.0, "транспорт", "4242"),
]


@router.post("/seed", response_model=DemoSeedResponse)
def seed_demo_data(
    reset: bool = Query(
        False,
        description="Удалить карты, транзакции и рекомендации пользователя и залить демо заново",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    has_cards = (
        db.query(Card).filter(Card.user_id == current_user.id).first() is not None
    )
    if has_cards and not reset:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="У пользователя уже есть карты. Повторите с параметром reset=true",
        )

    rec_removed = 0
    if reset:
        rec_removed = (
            db.query(Recommendation)
            .filter(Recommendation.user_id == current_user.id)
            .delete(synchronize_session=False)
        )
        db.query(Transaction).filter(Transaction.user_id == current_user.id).delete(
            synchronize_session=False
        )
        db.query(Card).filter(Card.user_id == current_user.id).delete(
            synchronize_session=False
        )
        db.commit()

    now = datetime.now()
    for c in DEMO_CARDS:
        db.add(
            Card(
                user_id=current_user.id,
                bank_name=c["bank_name"],
                card_name=c["card_name"],
                last4=c["last4"],
                cashback_rules=c["cashback_rules"],
                limit_monthly=c["limit_monthly"],
            )
        )
    db.commit()

    cards = db.query(Card).filter(Card.user_id == current_user.id).all()
    by_last4 = {c.last4: c for c in cards}

    n_tx = 0
    for idx, (days_ago, amount, category, last4) in enumerate(DEMO_TXN_SPEC):
        card = by_last4.get(last4)
        if not card:
            continue
        when = now - timedelta(days=days_ago, hours=idx % 5)
        cb = calculate_cashback(card, category, amount)
        db.add(
            Transaction(
                user_id=current_user.id,
                card_id=card.id,
                amount=amount,
                category=category,
                cashback_earned=cb,
                source="demo",
                external_id=f"demo-{current_user.id}-{idx}",
                occurred_at=when,
                created_at=when,
            )
        )
        n_tx += 1
    db.commit()

    return DemoSeedResponse(
        reset=reset,
        cards_created=len(DEMO_CARDS),
        transactions_created=n_tx,
        recommendations_removed=rec_removed,
    )

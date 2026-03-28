from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Transaction, Card
from schemas import (
    TransactionCreate,
    Transaction as TransactionSchema,
    TransactionBulkImport,
    TransactionBulkImportResult,
)
from auth import get_current_user
from cashback_calc import calculate_cashback

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", response_model=List[TransactionSchema])
def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(func.coalesce(Transaction.occurred_at, Transaction.created_at).desc())
        .all()
    )


@router.post("/", response_model=TransactionSchema)
def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Проверяем, что карта принадлежит пользователю
    card = db.query(Card).filter(
        Card.id == transaction.card_id,
        Card.user_id == current_user.id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Карта не найдена"
        )
    
    # Рассчитываем кэшбэк
    cashback_earned = calculate_cashback(card, transaction.category, transaction.amount)
    
    db_transaction = Transaction(
        user_id=current_user.id,
        card_id=transaction.card_id,
        amount=transaction.amount,
        category=transaction.category,
        cashback_earned=cashback_earned,
        source="manual",
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction


@router.post("/import", response_model=TransactionBulkImportResult)
def import_transactions(
    body: TransactionBulkImport,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Пакетная загрузка операций (как из выписки): сопоставление карты по last4, дедуп по external_id."""
    created = 0
    skipped = 0
    errors: List[str] = []
    user_cards = db.query(Card).filter(Card.user_id == current_user.id).all()
    by_last4 = {}
    for c in user_cards:
        by_last4.setdefault(c.last4, []).append(c)

    for i, item in enumerate(body.items):
        if item.external_id:
            exists = (
                db.query(Transaction)
                .filter(
                    Transaction.user_id == current_user.id,
                    Transaction.external_id == item.external_id,
                )
                .first()
            )
            if exists:
                skipped += 1
                continue
        cards = by_last4.get(item.card_last4)
        if not cards:
            errors.append(f"Строка {i + 1}: нет карты с last4={item.card_last4}")
            continue
        card = cards[0]
        cb = calculate_cashback(card, item.category, item.amount)
        db.add(
            Transaction(
                user_id=current_user.id,
                card_id=card.id,
                amount=item.amount,
                category=item.category,
                cashback_earned=cb,
                source="import",
                external_id=item.external_id,
                occurred_at=item.occurred_at,
            )
        )
        created += 1
    db.commit()
    return TransactionBulkImportResult(
        created=created, skipped_duplicates=skipped, errors=errors
    )

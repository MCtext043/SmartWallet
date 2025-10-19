from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Transaction, Card
from schemas import TransactionCreate, Transaction as TransactionSchema
from auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])


def calculate_cashback(card: Card, category: str, amount: float) -> float:
    """Рассчитывает кэшбэк для транзакции"""
    cashback_rules = card.cashback_rules or {}
    cashback_percentage = cashback_rules.get(category, cashback_rules.get("прочее", 0))
    
    if cashback_percentage == 0:
        return 0.0
    
    cashback_amount = (amount * cashback_percentage) / 100.0
    
    # Проверяем лимит кэшбэка
    if card.limit_monthly:
        # Здесь можно добавить логику проверки месячного лимита
        # Для MVP просто возвращаем рассчитанный кэшбэк
        pass
    
    return cashback_amount


@router.get("/", response_model=List[TransactionSchema])
def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Transaction).filter(Transaction.user_id == current_user.id).all()


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
    
    # Создаем транзакцию
    db_transaction = Transaction(
        user_id=current_user.id,
        card_id=transaction.card_id,
        amount=transaction.amount,
        category=transaction.category,
        cashback_earned=cashback_earned
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction

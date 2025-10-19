from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import User, Card
from schemas import BestCardResponse
from auth import get_current_user

router = APIRouter(prefix="/cashback", tags=["cashback"])


@router.get("/best-card", response_model=BestCardResponse)
def get_best_card_for_category(
    category: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Получаем все карты пользователя
    user_cards = db.query(Card).filter(Card.user_id == current_user.id).all()
    
    if not user_cards:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="У вас нет добавленных карт"
        )
    
    best_card = None
    best_cashback = 0
    
    # Ищем карту с максимальным кэшбэком для категории
    for card in user_cards:
        cashback_rules = card.cashback_rules or {}
        cashback_percentage = cashback_rules.get(category, cashback_rules.get("прочее", 0))
        
        if cashback_percentage > best_cashback:
            best_cashback = cashback_percentage
            best_card = card
    
    if not best_card:
        # Если нет карты для категории, берем карту с кэшбэком "прочее"
        for card in user_cards:
            cashback_rules = card.cashback_rules or {}
            cashback_percentage = cashback_rules.get("прочее", 0)
            
            if cashback_percentage > best_cashback:
                best_cashback = cashback_percentage
                best_card = card
                category = "прочее"
    
    if not best_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Не найдена подходящая карта"
        )
    
    return BestCardResponse(
        card_id=best_card.id,
        bank_name=best_card.bank_name,
        card_name=best_card.card_name,
        cashback_percentage=best_cashback,
        category=category
    )

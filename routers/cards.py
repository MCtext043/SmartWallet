from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Card
from schemas import CardCreate, Card as CardSchema
from auth import get_current_user

router = APIRouter(prefix="/cards", tags=["cards"])


@router.get("/", response_model=List[CardSchema])
def get_cards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Card).filter(Card.user_id == current_user.id).all()


@router.post("/", response_model=CardSchema)
def create_card(
    card: CardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_card = Card(
        user_id=current_user.id,
        bank_name=card.bank_name,
        card_name=card.card_name,
        last4=card.last4,
        cashback_rules=card.cashback_rules,
        limit_monthly=card.limit_monthly
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card


@router.get("/{card_id}", response_model=CardSchema)
def get_card(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    card = db.query(Card).filter(
        Card.id == card_id,
        Card.user_id == current_user.id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Карта не найдена"
        )
    
    return card

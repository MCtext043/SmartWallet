from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import requests
from database import get_db
from models import User, Recommendation, Card, Transaction
from schemas import Recommendation as RecommendationSchema
from auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/assistant", tags=["assistant"])


# Схемы для чата
class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


def get_user_context(current_user: User, db: Session) -> str:
    """Получает контекст пользователя для ассистента"""
    # Получаем карты пользователя
    user_cards = db.query(Card).filter(Card.user_id == current_user.id).all()
    
    # Получаем последние транзакции
    recent_transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.created_at.desc()).limit(5).all()
    
    context = f"Пользователь: {current_user.name}\n"
    context += f"Телефон: {current_user.phone}\n\n"
    
    if user_cards:
        context += "Карты пользователя:\n"
        for card in user_cards:
            cashback_rules = card.cashback_rules or {}
            rules_str = ", ".join([f"{k}: {v}%" for k, v in cashback_rules.items()])
            context += f"- {card.bank_name} {card.card_name} (****{card.last4}): {rules_str}\n"
        context += "\n"
    
    if recent_transactions:
        context += "Последние транзакции:\n"
        for trans in recent_transactions:
            context += f"- {trans.category}: {trans.amount}₽ (кэшбэк: {trans.cashback_earned}₽)\n"
    
    return context


@router.post("/chat", response_model=ChatResponse)
def chat_with_assistant(
    message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Чат с AI ассистентом по финансовой грамотности"""
    
    try:
        # Получаем контекст пользователя
        user_context = get_user_context(current_user, db)
        
        # Подготавливаем системное сообщение с контекстом
        system_message = f"""Ты учитель по финансовой грамотности, объясняй четко и понятно.
Ты помогаешь пользователю SmartWallet оптимизировать кэшбэк с карт.

Контекст пользователя:
{user_context}

Отвечай коротко и по делу. Если пользователь спрашивает про кэшбэк, используй информацию о его картах."""
        
        # Отправляем запрос к GigaChat API
        response = requests.post(
            "https://derendyaev.ru/api/gigachat/message",
            json={
                "model": "GigaChat:latest",
                "stream": False,
                "update_interval": 0,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message.message}
                ],
                "n": 1,
                "max_tokens": 256,
                "repetition_penalty": 1.0
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return ChatResponse(reply=response.text.strip())
        else:
            return ChatResponse(
                reply=f"Извините, произошла ошибка при обращении к ассистенту (код {response.status_code}). Попробуйте позже."
            )
            
    except requests.exceptions.ConnectionError:
        return ChatResponse(reply="Извините, не удается подключиться к ассистенту. Проверьте интернет-соединение.")
    except requests.exceptions.Timeout:
        return ChatResponse(reply="Извините, ассистент не отвечает. Попробуйте позже.")
    except Exception as e:
        return ChatResponse(reply=f"Произошла ошибка: {str(e)}")


@router.get("/recommendations", response_model=List[RecommendationSchema])
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Получаем последние рекомендации для пользователя
    recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id
    ).order_by(Recommendation.created_at.desc()).limit(3).all()
    
    # Если рекомендаций нет, создаем базовые
    if not recommendations:
        base_recommendations = [
            Recommendation(
                user_id=current_user.id,
                message="Добавьте карты с высоким кэшбэком для разных категорий трат",
                type="совет"
            ),
            Recommendation(
                user_id=current_user.id,
                message="Используйте карту с максимальным кэшбэком для каждой покупки",
                type="совет"
            ),
            Recommendation(
                user_id=current_user.id,
                message="Проверяйте лимиты кэшбэка перед крупными покупками",
                type="совет"
            )
        ]
        
        for rec in base_recommendations:
            db.add(rec)
        db.commit()
        
        recommendations = base_recommendations
    
    return recommendations

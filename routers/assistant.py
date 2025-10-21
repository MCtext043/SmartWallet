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


def clean_giga_response(response_text: str) -> str:
    """Очищает и форматирует ответ от GigaChat для корректного отображения"""
    try:
        # Пытаемся распарсить как JSON
        import json
        giga_data = json.loads(response_text)
        
        if isinstance(giga_data, dict):
            if "content" in giga_data:
                text = giga_data["content"]
            else:
                text = response_text
        else:
            text = response_text
    except (ValueError, TypeError):
        # Если не JSON, используем текст как есть
        text = response_text
    
    # Очищаем и форматируем текст
    text = text.strip()
    
    # Обрабатываем escape-последовательности
    text = text.replace('\\n', '\n')     # Переносы строк
    text = text.replace('\\"', '"')      # Кавычки
    text = text.replace('\\/', '/')      # Слэши
    text = text.replace('\\\\', '\\')    # Обратные слэши
    text = text.replace('\\t', '\t')     # Табуляция
    
    return text


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
            # Очищаем и форматируем ответ от GigaChat
            clean_reply = clean_giga_response(response.text)
            return ChatResponse(reply=clean_reply)
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


def generate_personalized_recommendations(current_user: User, db: Session) -> List[Recommendation]:
    """Генерирует персонализированные рекомендации на основе данных пользователя"""
    
    # Получаем данные пользователя
    user_cards = db.query(Card).filter(Card.user_id == current_user.id).all()
    recent_transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.created_at.desc()).limit(10).all()
    
    recommendations = []
    
    # 1. Анализ карт
    if not user_cards:
        recommendations.append(Recommendation(
            user_id=current_user.id,
            message="Добавьте карты для получения кэшбэка и оптимизации трат",
            type="совет"
        ))
    elif len(user_cards) == 1:
        recommendations.append(Recommendation(
            user_id=current_user.id,
            message="Добавьте больше карт для разных категорий трат - это увеличит ваш кэшбэк",
            type="совет"
        ))
    
    # 2. Анализ транзакций и категорий
    if recent_transactions:
        # Анализ категорий трат
        category_spending = {}
        category_transactions = {}
        
        for trans in recent_transactions:
            category = trans.category
            category_spending[category] = category_spending.get(category, 0) + trans.amount
            category_transactions[category] = category_transactions.get(category, 0) + 1
        
        # Находим самую затратную категорию
        if category_spending:
            top_category, top_amount = max(category_spending.items(), key=lambda x: x[1])
            
            # Находим лучшую карту для этой категории
            best_card = None
            best_cashback = 0
            for card in user_cards:
                cashback_rules = card.cashback_rules or {}
                cashback_percentage = cashback_rules.get(top_category, 0)
                if cashback_percentage > best_cashback:
                    best_cashback = cashback_percentage
                    best_card = card
            
            if best_card and best_cashback > 0:
                potential_cashback = (top_amount * best_cashback) / 100
                recommendations.append(Recommendation(
                    user_id=current_user.id,
                    message=f"Для категории '{top_category}' ({top_amount:.0f}₽) используйте {best_card.bank_name} ({best_cashback}%) - получите {potential_cashback:.0f}₽ кэшбэка",
                    type="совет"
                ))
        
        # 3. Анализ кэшбэка
        total_spent = sum(trans.amount for trans in recent_transactions)
        total_cashback = sum(trans.cashback_earned for trans in recent_transactions)
        cashback_ratio = (total_cashback / total_spent * 100) if total_spent > 0 else 0
        
        if cashback_ratio < 1:  # Менее 1% кэшбэка
            recommendations.append(Recommendation(
                user_id=current_user.id,
                message=f"Ваш кэшбэк составляет {cashback_ratio:.1f}% от трат. Рассмотрите карты с более высоким кэшбэком",
                type="совет"
            ))
        
        # 4. Анализ неиспользуемых категорий
        if user_cards:
            all_categories = set()
            for card in user_cards:
                if card.cashback_rules:
                    all_categories.update(card.cashback_rules.keys())
            
            used_categories = set(category_spending.keys())
            unused_categories = all_categories - used_categories
            
            if unused_categories:
                recommendations.append(Recommendation(
                    user_id=current_user.id,
                    message=f"Используйте карты для категорий: {', '.join(unused_categories)} - они дают дополнительный кэшбэк",
                    type="совет"
                ))
    
    # 5. Базовые рекомендации, если мало персональных
    if len(recommendations) < 2:
        recommendations.extend([
            Recommendation(
                user_id=current_user.id,
                message="Проверяйте лимиты кэшбэка перед крупными покупками",
                type="совет"
            ),
            Recommendation(
                user_id=current_user.id,
                message="Используйте разные карты для разных категорий трат",
                type="совет"
            )
        ])
    
    # 6. Рекомендации по лимитам
    for card in user_cards:
        if card.limit_monthly:
            monthly_cashback = db.query(Transaction).filter(
                Transaction.user_id == current_user.id,
                Transaction.card_id == card.id
            ).all()
            
            current_cashback = sum(trans.cashback_earned for trans in monthly_cashback)
            if current_cashback > card.limit_monthly * 0.8:  # Близко к лимиту
                recommendations.append(Recommendation(
                    user_id=current_user.id,
                    message=f"Внимание: кэшбэк по карте {card.bank_name} ({current_cashback:.0f}₽ из {card.limit_monthly:.0f}₽) близок к лимиту",
                    type="акция"
                ))
    
    return recommendations[:3]  # Возвращаем максимум 3 рекомендации


@router.get("/recommendations", response_model=List[RecommendationSchema])
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получает персонализированные рекомендации на основе данных пользователя"""
    
    # Проверяем, есть ли недавние рекомендации (не старше 1 дня)
    from datetime import datetime, timedelta
    recent_recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id,
        Recommendation.created_at >= datetime.now() - timedelta(days=1)
    ).order_by(Recommendation.created_at.desc()).limit(3).all()
    
    # Если есть свежие рекомендации, возвращаем их
    if recent_recommendations:
        return recent_recommendations
    
    # Генерируем новые персонализированные рекомендации
    new_recommendations = generate_personalized_recommendations(current_user, db)
    
    # Сохраняем в базу данных
    for rec in new_recommendations:
        db.add(rec)
    db.commit()
    
    return new_recommendations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Recommendation, Card, Transaction
from schemas import Recommendation as RecommendationSchema
from auth import get_current_user

router = APIRouter(prefix="/assistant", tags=["assistant"])


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

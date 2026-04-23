"""
Пример улучшенного эндпоинта /assistant/recommendations
с персонализированными рекомендациями на основе данных пользователя
"""

def get_personalized_recommendations(current_user: User, db: Session) -> List[RecommendationSchema]:
    """Персонализированные рекомендации на основе данных пользователя"""
    
    # Получаем данные пользователя
    user_cards = db.query(Card).filter(Card.user_id == current_user.id).all()
    recent_transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.created_at.desc()).limit(10).all()
    
    recommendations = []
    
    # Анализ карт
    if not user_cards:
        recommendations.append(Recommendation(
            user_id=current_user.id,
            message="Добавьте карты для получения кэшбэка",
            type="совет"
        ))
    elif len(user_cards) == 1:
        recommendations.append(Recommendation(
            user_id=current_user.id,
            message="Добавьте больше карт для разных категорий трат",
            type="совет"
        ))
    
    # Анализ транзакций
    if recent_transactions:
        # Анализ категорий трат
        category_spending = {}
        for trans in recent_transactions:
            category_spending[trans.category] = category_spending.get(trans.category, 0) + trans.amount
        
        # Находим самую затратную категорию
        top_category = max(category_spending.items(), key=lambda x: x[1])
        
        # Находим лучшую карту для этой категории
        best_card = None
        best_cashback = 0
        for card in user_cards:
            cashback_rules = card.cashback_rules or {}
            cashback_percentage = cashback_rules.get(top_category[0], 0)
            if cashback_percentage > best_cashback:
                best_cashback = cashback_percentage
                best_card = card
        
        if best_card and best_cashback > 0:
            recommendations.append(Recommendation(
                user_id=current_user.id,
                message=f"Для категории '{top_category[0]}' используйте {best_card.bank_name} ({best_cashback}%)",
                type="совет"
            ))
        
        # Анализ кэшбэка
        total_cashback = sum(trans.cashback_earned for trans in recent_transactions)
        if total_cashback < 100:  # Менее 100 рублей кэшбэка
            recommendations.append(Recommendation(
                user_id=current_user.id,
                message="Рассмотрите карты с более высоким кэшбэком",
                type="совет"
            ))
    
    # Базовые рекомендации, если мало персональных
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
    
    return recommendations[:3]  # Возвращаем максимум 3 рекомендации

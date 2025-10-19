from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    phone: str
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    phone: str
    password: str


class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Card schemas
class CardBase(BaseModel):
    bank_name: str
    card_name: str
    last4: str
    cashback_rules: Dict[str, int]
    limit_monthly: float


class CardCreate(CardBase):
    pass


class Card(CardBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Transaction schemas
class TransactionBase(BaseModel):
    amount: float
    category: str


class TransactionCreate(TransactionBase):
    card_id: int


class Transaction(TransactionBase):
    id: int
    user_id: int
    card_id: int
    cashback_earned: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# Recommendation schemas
class RecommendationBase(BaseModel):
    message: str
    type: str


class Recommendation(RecommendationBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    phone: Optional[str] = None


# Cashback schemas
class BestCardResponse(BaseModel):
    card_id: int
    bank_name: str
    card_name: str
    cashback_percentage: int
    category: str

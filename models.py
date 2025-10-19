from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password_hash = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    
    cards = relationship("Card", back_populates="owner")
    transactions = relationship("Transaction", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")


class Card(Base):
    __tablename__ = "cards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    bank_name = Column(String)
    card_name = Column(String)
    last4 = Column(String(4))
    cashback_rules = Column(JSON)  # {"еда":5, "транспорт":3, "прочее":1}
    limit_monthly = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    
    owner = relationship("User", back_populates="cards")
    transactions = relationship("Transaction", back_populates="card")


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    card_id = Column(Integer, ForeignKey("cards.id"))
    amount = Column(Float)
    category = Column(String)
    cashback_earned = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="transactions")
    card = relationship("Card", back_populates="transactions")


class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    type = Column(String)  # "совет" / "акция"
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="recommendations")

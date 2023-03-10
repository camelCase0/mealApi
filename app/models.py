from datetime import date
from enum import Enum

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Float, Table
from sqlalchemy.orm import Session, relationship

from app.config import DATABASE_URL

from .database import Base

class Category(Enum):
    A = "Vegetables"
    B = "Fruits"
    C = "Cereals"
    D = "Tubers"
    E = "Legumes"
    F = "Dairy"
    G = "Meat"
    H = "Seafoods"
    I = "Sweeteners"
    J =  "Dishes"
    K =  "Nuts"
    L = "Condiments"
    M =  "Fluids" 

class Units(Enum):
    p = "pieces"
    ml = "ml"
    g = "g"

class Ingredients(Base):
    __tablename__ = 'ingredients'
    
    ingredient_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    ingredient_image = Column(String)
    category = Column(String, default=Category.A.name)
    measure = Column(String, default=Units.p.name)
    stored_amount = Column(Float, default=0.0)
    expiry_date = Column(DateTime, default=date)

    receipts = relationship("Receipts", back_populates="ingredients")

class Meal(Base):
    __tablename__ = "meal"

    meal_id = Column(Integer, primary_key=True, index=True)
    meal_name = Column(String)
    meal_image = Column(String)
    receipt = Column(String)
    difficulty = Column(Integer)

    receipts = relationship("Receipts", back_populates="meals")
    
class Receipts(Base):
    __tablename__ = 'receipts'

    rec_id = Column(Integer, primary_key=True, index=True)
    
    meal_id = Column(Integer, ForeignKey('meal.meal_id'))
    meals = relationship("Meal", back_populates="receipts")

    ingredient_id = Column(Integer, ForeignKey('ingredients.ingredient_id'))
    ingredients = relationship("Ingredients", back_populates="receipts")
    amount = Column(Float)
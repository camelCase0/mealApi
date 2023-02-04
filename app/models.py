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

# class Fridge(Base):
#     __tablename__ = "fridge"
#     ingredient_id = Column(Integer, ForeignKey("ingredients.ingredient_id"), primary_key=True)
#     ingredient = relationship("Ingredients", back_populates="fridge") 
#     amount = Column(Float)
#     expiry_date = Column(DateTime, default=datetime.utcnow())
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

    # meals = relationship("Meal", secondary="receipts", back_populates="ingredients")
    # donations = relationship("Donations", back_populates="ingredients")

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
    # ingredients = relationship("Ingredients", secondary="receipts", back_populates="meals")

# class Meal_Ingredient(Base):

#     meal_id = Column(Integer, ForeignKey="meal.meal_id")
#     ingredient_id = Column(Integer, ForeignKey="ingredients.id")


# class Donations(Base):
#     __tablename__ = 'donations'

#     record_id = Column(Integer, primary_key=True)
#     volume = Column(Integer)
#     date = Column(DateTime, default=datetime.utcnow())
    
#     user_id = Column(Integer, ForeignKey('users.id'))
#     user = relationship("User", back_populates="donations")
    
#     clinic_id = Column(Integer, ForeignKey('clinics.clinic_id'))
#     clinic = relationship("Clinics", back_populates="donations")


# class Clinics(Base):
#     __tablename__ = 'clinics'

#     clinic_id = Column(Integer, primary_key=True)
#     address = Column(String)
#     altitude = Column(Float)
#     longitude = Column(Float)

#     donations = relationship("Donations", back_populates="clinic")

#
# class AuthToken(Base):
#     __tablename__ = 'auth_token'
#
#     id = Column(Integer, primary_key=True)
#     token = Column(String)
#     user_id = Column(Integer, ForeignKey('users.id'))
#     created_at = Column(String, default=datetime.utcnow())
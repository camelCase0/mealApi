from datetime import date

from pydantic import BaseModel
from typing import List, Optional
from .models import Units, Category

class IngredientCreateForm(BaseModel):
    id: int
    name: str
    image: str
    category: Category
    stored_amount: float
    measure: Units
    expiry_date: date
    class Config:
        orm_mode = True

class IngredientUpdateForm(BaseModel):
    name: str
    image: str
    category: Category
    stored_amount: float
    measure: Units
    expiry_date: date
    class Config:
        orm_mode = True

class ReceiptCreateForm(BaseModel):
    ingredient_id: int
    amount: float
    class Config:
        orm_mode = True

class MealCreateForm(BaseModel):
    id: int 
    name: str
    image: str
    receipt: str
    difficulty: int
    class Config:
        orm_mode = True

class IngredientGetForm(BaseModel):
    ingredient_id: int
    name: str
    ingredient_image: str
    category: Category
    stored_amount: float
    measure: Units
    expiry_date: date
    # meals: List[MealBase]

    class Config:
        orm_mode = True

class ReceiptGetForm(BaseModel):
    meal_id: int
    # meals: MealGetForm
    ingredient_id: int
    # ingredients: IngredientGetForm
    amount: float
    class Config:
        orm_mode = True

class ReceiptsGetForMeal(BaseModel):
    name: str
    ingredient_image: str
    category: Category
    stored_amount: float
    measure: Units
    expiry_date: date
    amount: float

class MealGetBaseForm(BaseModel):
    meal_id: int 
    meal_name: str
    meal_image: str
    receipt: str
    difficulty: int

    class Config:
        orm_mode = True

class MealGetForm(BaseModel):
    meal_id: int 
    meal_name: str
    meal_image: str
    receipt: str
    difficulty: int
    receipts: List[ReceiptsGetForMeal]

    class Config:
        orm_mode = True

class MealGetAllForm(BaseModel):
    meal_id: int 
    meal_name: str
    meal_image: str
    difficulty: int
    class Config:
        orm_mode = True
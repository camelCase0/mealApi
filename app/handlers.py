import uuid
from datetime import date, datetime
from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Body, Depends, HTTPException
from starlette import status

from app.models import Category, Units, Ingredients, Meal, Base, Receipts
from app.forms import IngredientCreateForm, IngredientUpdateForm, IngredientGetForm, MealCreateForm, MealGetForm, ReceiptCreateForm, ReceiptGetForm, ReceiptsGetForMeal, MealGetAllForm
from .database import SessionLocal, engine
from . import crud
Base.metadata.create_all(bind=engine)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def ingredient_refactor(ingredient):
    obj = ingredient
    for el in obj:
        el.category = Category[el.category].value
        el.measure = Units[el.measure].value
    return obj

@router.get("/", tags=["temp"])
def index():
    return 200

@router.post("/ingredient", tags=["ingredient"],status_code=201)
def create_ingredient(ing_form:IngredientCreateForm = Body(...), database=Depends(get_db)):
    new_ingredient = Ingredients(
        ingredient_id = ing_form.id,
        name = ing_form.name,
        ingredient_image = ing_form.image,
        category = ing_form.category.name,
        stored_amount = ing_form.stored_amount,
        measure = ing_form.measure.name,
        expiry_date = ing_form.expiry_date
    )
    exist = database.query(Ingredients.ingredient_id).filter(Ingredients.name == ing_form.name).one_or_none()
    if exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="such product is already exists")
    
    database.add(new_ingredient)
    database.commit()
    database.refresh(new_ingredient)
    return status.HTTP_201_CREATED

@router.put("/ingredient/{id}", tags=["ingredient"])
def update_ingredient(id:int, ing_form:IngredientUpdateForm = Body(...), database=Depends(get_db)):
    exist = database.query(Ingredients).filter(Ingredients.ingredient_id == id)
    if not exist.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no such product")
    exist.update({
        'name' : ing_form.name,
        'ingredient_image' : ing_form.image,
        'category' : ing_form.category.name,
        'stored_amount' : ing_form.stored_amount,
        'measure' : ing_form.measure.name,
        'expiry_date': ing_form.expiry_date
    })
    database.commit()
    return 200

@router.get("/ingredient/{id}", tags=['ingredient'], response_model=IngredientGetForm)
def get_ingredient_by_id(id:int, database=Depends(get_db)):
    exist = database.query(Ingredients).filter(Ingredients.ingredient_id == id).one_or_none()
    if not exist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no such product")
    exist.category = Category[exist.category].value
    exist.measure = Units[exist.measure].value
    print(vars(exist))
    return exist

@router.delete("/ingredient/{id}", tags=['ingredient'])
def delete_ingredient_by_id(id:int, database=Depends(get_db)):
    ingr = database.query(Ingredients).filter(Ingredients.ingredient_id == id).one_or_none()
    if not ingr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such item")
    database.delete(ingr)
    database.commit()
    return 200

@router.get("/ingredient", tags=['ingredient'], response_model=List[IngredientGetForm])
def get_all_ingredients(database=Depends(get_db)):
    ingreds = database.query(Ingredients).all()
    if not ingreds:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such item")
    return ingredient_refactor(ingreds)

@router.get("/fridge", tags=['ingredient'], response_model=List[IngredientGetForm])
def get_existing_ingredients(database=Depends(get_db)):
    ingreds = database.query(Ingredients).filter(Ingredients.stored_amount > 0).all()
    if not ingreds:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such item")
    return ingredient_refactor(ingreds)

# M E A L _________________
@router.post("/meal", tags=['meal'], status_code=201)
def create_meal(cmf: MealCreateForm = Body(...), database=Depends(get_db)):
    exist = database.query(Meal).filter(Meal.meal_name == cmf.name).one_or_none()
    if exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="already exists")
    new_meal = Meal(
        meal_id = cmf.id,
        meal_name = cmf.name,
        meal_image = cmf.image,
        receipt = cmf.receipt,
        difficulty = cmf.difficulty
    )
    database.add(new_meal)
    database.commit()
    database.refresh(new_meal)
    return 201

@router.get("/meal/{id}", tags=['meal'], response_model=MealGetForm)
def get_meal_by_id(id:int, database=Depends(get_db)):
    meal = database.query(Meal).filter(Meal.meal_id == id).first()
    if not meal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such item")

    ingreds = []
    for el in meal.receipts:
        ing = database.query(Ingredients).filter(Ingredients.ingredient_id == el.ingredient_id).first()
        rec_amount = database.query(Receipts).filter(Receipts.ingredient_id == el.ingredient_id,Receipts.meal_id == el.meal_id ).first()
        rec = ReceiptsGetForMeal(
            name = ing.name,
            ingredient_image = ing.ingredient_image,
            category = Category[ing.category].value,
            stored_amount = ing.stored_amount,
            measure=  Units[ing.measure].value,
            expiry_date= ing.expiry_date,
            amount = rec_amount.amount
        )
        ingreds.append(rec)

    res_meal = MealGetForm(
        meal_id = meal.meal_id, 
        meal_name = meal.meal_name,
        meal_image = meal.meal_image,
        receipt = meal.receipt,
        difficulty = meal.difficulty,
        receipts = ingreds
    )
    return res_meal

@router.get("/meal/", tags=['meal'], response_model=List[MealGetForm]) #MealGetAllForm
def get_meals(database=Depends(get_db)):
    meals = database.query(Meal).all()
    res_meals = []
    for meal in meals:
        ingreds = []
        for el in meal.receipts:
            ing = database.query(Ingredients).filter(Ingredients.ingredient_id == el.ingredient_id).first()
            rec_amount = database.query(Receipts).filter(Receipts.ingredient_id == el.ingredient_id,Receipts.meal_id == el.meal_id ).first()
            rec = ReceiptsGetForMeal(
                name = ing.name,
                ingredient_image = ing.ingredient_image,
                category = Category[ing.category].value,
                stored_amount = ing.stored_amount,
                measure=  Units[ing.measure].value,
                expiry_date= ing.expiry_date,
                amount = rec_amount.amount
            )
            ingreds.append(rec)

        res_meal = MealGetForm(
            meal_id = meal.meal_id, 
            meal_name = meal.meal_name,
            meal_image = meal.meal_image,
            receipt = meal.receipt,
            difficulty = meal.difficulty,
            receipts = ingreds
        )
        res_meals.append(res_meal)
    return res_meals

# @router.get("/meal-to-cook", tags=['meal'], response_model=List[MealGetAllForm])
# def get_awailable_meals()

@router.delete("/meal/{id}", tags=['meal'])
def delete_meal_by_Id(id:int, database=Depends(get_db)):
    exist = database.query(Meal).filter(Meal.meal_id == id).one_or_none()
    if not exist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such item")
    database.delete(exist)
    database.commit()
    
    recepts = database.query(Receipts).filter(Receipts.meal_id == id).all()
    for el in recepts:
        database.delete(el)
        database.commit()
    return 200

# R E C E I P T __ __ __ __ __
@router.post("/receipt/{id}", tags=['receipt'], status_code=201)
def create_receipt_by_mealId(id:int, list_form: List[ReceiptCreateForm] = Body(...), database=Depends(get_db)):
    exist = database.query(Meal).filter(Meal.meal_id == id).one_or_none()
    if not exist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such item")
    for form in list_form:
        new_rec = Receipts(
            meal_id = id,
            ingredient_id= form.ingredient_id,
            amount= form.amount
        )
        database.add(new_rec)
        database.commit()
    return 201

@router.delete("/receipt/{id}", tags=['receipt'], status_code=200)
def delete_receipt_by_mealId(id:int, database=Depends(get_db)):
    exist = database.query(Meal).filter(Meal.meal_id == id).one_or_none()
    if not exist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such item")

    exist = database.query(Receipts).filter(Receipts.meal_id == id).all()
    for el in exist:
        database.delete(el)
        database.commit()
    return 200

@router.get("/receipt", tags=['receipt'], response_model=List[ReceiptGetForm])
def get_all_receipts(database=Depends(get_db)):
    rceps = database.query(Receipts).all()
    return rceps


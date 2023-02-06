import uuid
from datetime import date, datetime
from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Body, Depends, HTTPException
from starlette import status

# from app.forms import UserLoginForm, UserCreateForm, UserGetForm, DonationCreateForm, DonationGetForm, ClinicCreateForm, ClinicGetForm
from app.models import Category, Units, Ingredients, Meal, Base, Receipts
from app.forms import IngredientCreateForm, IngredientUpdateForm, IngredientGetForm, MealCreateForm, MealGetForm, ReceiptCreateForm, ReceiptGetForm, ReceiptsGetForMeal
# from app.utils import get_password_hash
# from app.auth import check_auth_token

# from app.auth.auth_bearer import JWTBearer
# from app.auth.auth_handler import signJWT, decodeJWT
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
    # ingredients = cmf.ingredients
    # for ing in ingredients:
    #     rec = Receipts(
    #         meal_id = new_meal.meal_id,
    #         ingredient_id = ing.ingredient_id,
    #         amount = ing.amount
    #     )
    #     database.add(rec)
    #     database.commit()
    return 201

@router.get("/meal/{id}", tags=['meal'], response_model=MealGetForm)
def get_meal_by_id(id:int, database=Depends(get_db)):
    meal = database.query(Meal).filter(Meal.meal_id == id).first()
    if not meal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such item")
    # print(vars(meal.ingredients))
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
    # ingreds = ingredient_refactor(ingreds)
    print(vars(ing))

    res_meal = MealGetForm(
        meal_id = meal.meal_id, 
        meal_name = meal.meal_name,
        meal_image = meal.meal_image,
        receipt = meal.receipt,
        difficulty = meal.difficulty,
        receipts = ingreds
    )
    return res_meal

# @router.put("")
# @router.delete()
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
    for el in rceps:
        el.ingredients.category = Category[el.ingredients.category].value
        el.ingredients.measure = Units[el.ingredients.measure].value
    return rceps

# @router.post("/register", tags=["user"], name='user:create', status_code=201)#dependencies=[Depends(JWTBearer())],
# def create_user(userform: UserCreateForm = Body(...), database: Session = Depends(get_db), token=Depends(JWTBearer())):
#     loged_user = crud.get_user_by_token(database, token)
   
#     if not loged_user.status == Status.A.name:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin is permited!")

#     exists_user = database.query(User.id).filter(User.email == userform.email).one_or_none()
#     if exists_user:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

#     crud.create_user(database, userform, loged_user.id)
    
#     return status.HTTP_201_CREATED


# @router.post("/login", tags=["user"])
# def user_login(user_form: UserLoginForm = Body(...), database=Depends(get_db)):

#     user = database.query(User).filter(User.email == user_form.email).one_or_none()
#     if not user or get_password_hash(user_form.password) != user.password:
#         #DEBUGG
#         if user_form.email == "a":         #REMOVE IN PROD
#             crud.create_admin(database)    #REMOVE IN PROD
#             return status.HTTP_201_CREATED #REMOVE IN PROD

#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email/password is incorect")
#     return signJWT(user.id)

# @router.get('/users', tags=["user"], response_model=List[UserGetForm],dependencies=[Depends(JWTBearer())], name='user:get_all')#, dependencies=[Depends(JWTBearer())]
# def get_all_user(database=Depends(get_db)):
#     users = crud.get_all_users(database)
#     for user in users:
#         user.status = Status[user.status]
#         user.blood_type = Blood_type[user.blood_type]
#     return users

# @router.get('/user', tags=["user"], response_model=UserGetForm, dependencies=[Depends(JWTBearer())], name='curent_user:get')
# def get_curent_user(database=Depends(get_db), token=Depends(JWTBearer())):
#     user = crud.get_user_by_token(database, token)
    
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No such user")

#     user.status = Status[user.status].value
#     user.blood_type = Blood_type[user.blood_type].value
#     return user

# @router.get('/user/{user_id}', tags=["user"], response_model=UserGetForm, name='user:get')
# def get_user(user_id: int, database=Depends(get_db), token=Depends(JWTBearer())):

#     loged_user = crud.get_user_by_token(database, token) 
#     if not loged_user.status == Status.A.name:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin is permited!")

#     user = crud.get_user_by_id(database, user_id)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No such user")
#     user.status = Status[user.status]
#     user.blood_type = Blood_type[user.blood_type]
#     return user

# @router.delete('/user/{user_id}', tags=["user"], name='user:delete by id', status_code=200)
# def delete_user(user_id: int, database=Depends(get_db), token=Depends(JWTBearer())):
#     loged_user = crud.get_user_by_token(database, token)
#     if not loged_user.status == Status.A.name:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin is permited!")
    
#     user = crud.get_user_by_id(database, user_id)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such user")

#     return crud.delete_user_by_id(database, user_id)
     

# # D  O  N  A  T  I  O  N  S
# @router.get('/donations', tags=["donations"], response_model=List[DonationGetForm],dependencies=[Depends(JWTBearer())], name='donate:get all')# dependencies=[Depends(JWTBearer())],
# def get_all_donation(database=Depends(get_db)):

#     dons = database.query(Donations).order_by(Donations.date.desc()).all()
#     if not dons:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

#     for don in dons:
#         don.user.blood_type = Blood_type[don.user.blood_type]
#     return dons

# @router.post('/donations', tags=["donations"], status_code=201, dependencies=[Depends(JWTBearer())], name='donate:create') #dependencies=[Depends(JWTBearer())],
# def create_donation(donate_form: DonationCreateForm = Body(...), database=Depends(get_db)):
    
#     record = database.query(Donations).filter(Donations.user_id == donate_form.user_id).order_by(Donations.date.desc()).first()
#     cur_date = datetime.now()

#     if record:
#         next_time = datetime(year=record.date.year + int(record.date.month / 12), month=(record.date.month+2)%12, day=record.date.day, hour=record.date.hour, minute=record.date.minute)
#         if (next_time>cur_date):
#             raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Donor has donated resently. Donate_after {next_time}")
#     # CHECK ON INPUT DONATE_FORM DATA
#     if not crud.get_user_by_id(database, donate_form.user_id) or not crud.get_clinic_by_id(database, donate_form.clinic_id): 
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Wrong Body')
        
#     new_record = Donations(
#         user_id=donate_form.user_id,
#         volume=donate_form.volume,
#         clinic_id=donate_form.clinic_id
#     )
#     database.add(new_record)
#     database.commit()

#     crud.update_user_volume(database, donate_form.volume, donate_form.user_id)
    
#     return {'created_record':new_record.date, 'user_id':new_record.user_id}


# # C L I N I C -------------------------------------------------------------------------------------------------
# @router.post('/clinic',tags=['clinic'], status_code=201, name="clinic:create")
# def create_clinic(clinic_form: ClinicCreateForm = Body(...), database=Depends(get_db), token=Depends(JWTBearer())):
#     loged_user = crud.get_user_by_token(database, token)
#     if not loged_user.status == Status.A.name:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin is permited!")

#     clinic = database.query(Clinics).filter(Clinics.address == clinic_form.address).one_or_none()
#     if clinic:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Address already registered")
#     crud.create_clinic(database, clinic_form)
#     return status.HTTP_201_CREATED

# @router.delete('/clinic/{cl_id}',tags=['clinic'],status_code=200, name="clinic:delete")
# def delete_clinic(cl_id:int, database=Depends(get_db), token=Depends(JWTBearer())):
#     loged_user = crud.get_user_by_token(database, token)
#     if not loged_user.status == Status.A.name:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin is permited!")

#     clinic = crud.get_clinic_by_id(database, cl_id)
#     if not clinic:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No clinics with such id")
#     crud.delete_clinic(database, cl_id)
#     return clinic

# @router.get('/clinics', tags=['clinic'], response_model=List[ClinicGetForm], name="clinic:get all")
# def get_all_clinic(database=Depends(get_db)):
#     clinics = database.query(Clinics).all()
#     if not clinics:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No clinics in DB")
#     return clinics


# @router.get('/clinic/{cl_id}', tags=['clinic'], response_model=ClinicGetForm, name="clinic:get by id")
# def get_clinic(cl_id:int, database=Depends(get_db)):
#     clinic = crud.get_clinic_by_id(database, cl_id)
#     if not clinic:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No clinics with such id")
#     return clinic

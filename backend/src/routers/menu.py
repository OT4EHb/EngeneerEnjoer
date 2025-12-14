# src/routers/menu.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from database import get_db
from services.menu_service import MenuService
from schemas.menu import (
    Category, CategoryCreate, CategoryUpdate,
    Dish, DishCreate, DishUpdate, DishWithCategory, MenuResponse
)

router = APIRouter(prefix="/menu", tags=["menu"])

# Category endpoints
@router.post("/categories", response_model=Category)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    return MenuService.create_category(db, category)

@router.get("/categories", response_model=List[Category])
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return MenuService.get_categories(db, skip, limit)

@router.get("/categories/{category_id}", response_model=Category)
def get_category(
    category_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    category = MenuService.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/categories/{category_id}", response_model=Category)
def update_category(
    category_id: uuid.UUID,
    category: CategoryUpdate,
    db: Session = Depends(get_db)
):
    updated = MenuService.update_category(db, category_id, category)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated

@router.delete("/categories/{category_id}")
def delete_category(
    category_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    deleted = MenuService.delete_category(db, category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}

# Dish endpoints
@router.post("/dishes", response_model=Dish)
def create_dish(
    dish: DishCreate,
    db: Session = Depends(get_db)
):
    return MenuService.create_dish(db, dish)

@router.get("/dishes", response_model=List[DishWithCategory])
def get_dishes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category_id: Optional[uuid.UUID] = Query(None),
    available_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    return MenuService.get_dishes(db, skip, limit, category_id, available_only)

@router.get("/dishes/{dish_id}", response_model=DishWithCategory)
def get_dish(
    dish_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    dish = MenuService.get_dish(db, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish

@router.put("/dishes/{dish_id}", response_model=Dish)
def update_dish(
    dish_id: uuid.UUID,
    dish: DishUpdate,
    db: Session = Depends(get_db)
):
    updated = MenuService.update_dish(db, dish_id, dish)
    if not updated:
        raise HTTPException(status_code=404, detail="Dish not found")
    return updated

@router.delete("/dishes/{dish_id}")
def delete_dish(
    dish_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    deleted = MenuService.delete_dish(db, dish_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Dish not found")
    return {"message": "Dish deleted successfully"}

# Menu endpoints
@router.get("/", response_model=MenuResponse)
def get_full_menu(db: Session = Depends(get_db)):
    menu = MenuService.get_full_menu(db)
    return MenuResponse(**menu)

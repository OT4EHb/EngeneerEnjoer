# src/routers/orders.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import uuid
from database import get_db
from services.order_service import OrderService
from schemas.orders import Order, OrderCreate, OrderUpdate

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=Order)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db)
):
    try:
        return OrderService.create_order(db, order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Order])
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    return OrderService.get_orders(db, skip, limit, status, date_from)

@router.get("/{order_id}", response_model=Order)
def get_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    order = OrderService.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/{order_id}", response_model=Order)
def update_order(
    order_id: uuid.UUID,
    order: OrderUpdate,
    db: Session = Depends(get_db)
):
    updated = OrderService.update_order(db, order_id, order)
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated

@router.delete("/{order_id}")
def delete_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    deleted = OrderService.delete_order(db, order_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}

@router.get("/statistics/daily")
def get_daily_statistics(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db)
):
    return OrderService.get_order_statistics(db, start_date, end_date)

# src/routers/reports.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from database import get_db
from services.report_service import ReportService
from schemas.reports import SalesReport

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/sales", response_model=SalesReport)
def get_sales_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db)
):
    return ReportService.get_sales_report(db, start_date, end_date)

@router.get("/categories")
def get_category_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db)
):
    return ReportService.get_category_report(db, start_date, end_date)

@router.get("/daily-revenue")
def get_daily_revenue_report(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    return ReportService.get_daily_revenue_report(db, days)

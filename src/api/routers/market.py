from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, desc, asc
from src.database import get_db
from src.models.schema import IndexSnapshot, ForeignTrading
from datetime import datetime
from src.api.schemas import (
    IndexOverviewResponse, 
    TopImpactResponse, 
    ForeignTradingResponse,
    SectorPerformanceResponse
)
from src.cache.state import SYSTEM_STATUS

router = APIRouter(prefix="/api/v1", tags=["Market Data"])

@router.get("/system/status")
def get_system_status():
    return SYSTEM_STATUS

@router.get("/overview", response_model=IndexOverviewResponse)
def get_overview(db: Session = Depends(get_db)):
    """Lấy thông tin tổng quan điểm số mới nhất."""
    snapshot = db.query(IndexSnapshot).order_by(desc(IndexSnapshot.trading_date)).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="No overview data found")
    return snapshot

def get_active_session_date(db: Session):
    """
    Clock-based Session Guard:
    - Trước 09:15: Luôn dùng ngày của phiên đóng cửa gần nhất (Last Closed Session).
    - Sau 09:15: Nếu ngày today() có dữ liệu (turnover > 0), có thể dùng today().
    - Trả về: String 'YYYY-MM-DD'
    """
    now = datetime.now()
    today = now.date().isoformat()
    
    # 1. Tìm ngày gần nhất có dữ liệu (Check cả 2 bảng để tránh lỗi khi 1 bên đang nạp dở)
    latest_query = text("""
        SELECT MAX(trading_date) FROM (
            SELECT trading_date FROM market_prices WHERE trading_date < :today
            UNION ALL
            SELECT trading_date FROM foreign_trading WHERE trading_date < :today
        ) AS combined_dates
    """)
    last_date = db.execute(latest_query, {"today": today}).scalar()
    
    # Nếu đang trước 9:15 AM -> Force dùng phiên cũ gần nhất
    if now.hour < 9 or (now.hour == 9 and now.minute < 15):
        return last_date or today
        
    # 2. Sau 9:15 AM -> Check xem phiên hôm nay đã có data chưa
    check_query = text("SELECT COUNT(*) FROM market_prices WHERE trading_date = :today AND price > 0")
    count = db.execute(check_query, {"today": today}).scalar()
    
    if count > 50: 
        return today
    else:
        return last_date or today

@router.get("/top-impact", response_model=TopImpactResponse)
def get_top_impact(limit: int = 10, db: Session = Depends(get_db)):
    """Lọc top tác động từ market_prices & stocks (impact_metrics view)."""
    active_date = get_active_session_date(db)
    
    positive_query = text("SELECT symbol, sector, price, ref_price, change_percent, impact_value FROM impact_metrics WHERE impact_value > 0.001 AND trading_date = :dt ORDER BY impact_value DESC LIMIT :limit")
    positive_rows = db.execute(positive_query, {"limit": limit, "dt": active_date}).fetchall()
    
    negative_query = text("SELECT symbol, sector, price, ref_price, change_percent, impact_value FROM impact_metrics WHERE impact_value < -0.001 AND trading_date = :dt ORDER BY impact_value ASC LIMIT :limit")
    negative_rows = db.execute(negative_query, {"limit": limit, "dt": active_date}).fetchall()
    
    return {
        "positive": [dict(row._mapping) for row in positive_rows],
        "negative": [dict(row._mapping) for row in negative_rows]
    }

@router.get("/foreign-trading", response_model=ForeignTradingResponse)
def get_foreign_trading(limit: int = 10, db: Session = Depends(get_db)):
    """Lấy top mua/bán ròng của khối ngoại (ngày đầy đủ nhất)."""
    # Use max trading_date from foreign_trading specifically to handle weekends/delays
    from sqlalchemy.sql import func
    active_date = db.query(func.max(ForeignTrading.trading_date)).scalar()
    
    if not active_date:
        return {"top_buy": [], "top_sell": [], "total_net_val": 0.0}

    top_buy = db.query(ForeignTrading).filter(ForeignTrading.trading_date == active_date).order_by(desc(ForeignTrading.net_val)).limit(limit).all()
    top_sell = db.query(ForeignTrading).filter(ForeignTrading.trading_date == active_date).order_by(asc(ForeignTrading.net_val)).limit(limit).all()
    
    b = db.execute(text("SELECT SUM(f_buy_val) FROM foreign_trading WHERE trading_date = :d"), {"d": active_date}).scalar() or 0.0
    s = db.execute(text("SELECT SUM(f_sell_val) FROM foreign_trading WHERE trading_date = :d"), {"d": active_date}).scalar() or 0.0
    
    return {
        "top_buy": top_buy,
        "top_sell": top_sell,
        "total_net_val": float(b - s)
    }

@router.get("/sector-performance", response_model=SectorPerformanceResponse)
def get_sector_performance(db: Session = Depends(get_db)):
    """Lấy hiệu suất ngành (Tăng/giảm trung bình)."""
    query = text("SELECT trading_date, sector, avg_change, total_stocks FROM sector_performance_metrics WHERE trading_date = (SELECT MAX(trading_date) FROM sector_performance_metrics) AND sector IS NOT NULL ORDER BY avg_change DESC")
    rows = db.execute(query).fetchall()
    return {"sectors": [dict(row._mapping) for row in rows]}

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.database import get_db
from src.api.schemas import ReportGenerateRequest, ReportGenerateResponse
from src.services.ai_engine import AIEngine
from src.models import (
    DailyReportInput, MarketIndex, MarketBreadth, 
    ForeignTrading, SectorPerformance
)
from src.api.dependencies import limiter

router = APIRouter(prefix="/api/v1/report", tags=["Report"])

@router.post("/generate", response_model=ReportGenerateResponse)
@limiter.limit("5/minute")
async def generate_report(request: Request, payload: ReportGenerateRequest, db: Session = Depends(get_db)):
    """
    Kích hoạt AIEngine để tạo báo cáo.
    Nhận Manual Override từ frontend (Next.js) và kết hợp dữ liệu DB thực tế.
    """
    import asyncio
    from src.database import SessionLocal

    # 1. Fetch Index Data (Initial query to get the date)
    index_row = db.execute(text("SELECT * FROM index_snapshot ORDER BY trading_date DESC LIMIT 1")).fetchone()
    if not index_row:
        raise HTTPException(status_code=404, detail="No market data available in DB")
    
    t_date = index_row.trading_date
    f_date = db.execute(text("SELECT MAX(trading_date) FROM foreign_trading")).scalar() or t_date

    # 2. Execute Independent Queries Sequentially (Fast enough to avoid pool exhaustion)
    pos_rows = db.execute(text("SELECT symbol, change_percent FROM impact_metrics WHERE trading_date = :d ORDER BY impact_value DESC LIMIT 3"), {"d": t_date}).fetchall()
    neg_rows = db.execute(text("SELECT symbol, change_percent FROM impact_metrics WHERE trading_date = :d ORDER BY impact_value ASC LIMIT 3"), {"d": t_date}).fetchall()
    sector_rows = db.execute(text("SELECT sector, avg_change, total_stocks, top_symbols FROM sector_performance_metrics WHERE trading_date = :d ORDER BY avg_change DESC"), {"d": t_date}).fetchall()
    
    f_total_buy = db.execute(text("SELECT SUM(f_buy_val) FROM foreign_trading WHERE trading_date = :d"), {"d": f_date}).scalar() or 0.0
    f_total_sell = db.execute(text("SELECT SUM(f_sell_val) FROM foreign_trading WHERE trading_date = :d"), {"d": f_date}).scalar() or 0.0
    
    top_buy_rows = db.execute(text("SELECT symbol, net_val FROM foreign_trading WHERE trading_date = :d AND net_val > 0 ORDER BY net_val DESC LIMIT 3"), {"d": f_date}).fetchall()
    top_sell_rows = db.execute(text("SELECT symbol, net_val FROM foreign_trading WHERE trading_date = :d AND net_val < 0 ORDER BY net_val ASC LIMIT 3"), {"d": f_date}).fetchall()

    impact_pos = [f"{r.symbol} (+{r.change_percent}%)" for r in pos_rows]
    impact_neg = [f"{r.symbol} ({r.change_percent}%)" for r in neg_rows]

    # 3. Process Sectors (Top 3 Gainers & Top 3 Losers)
    valid_sectors = [sr for sr in sector_rows if sr.sector]
    top_3_gainers = valid_sectors[:3]
    top_3_losers = valid_sectors[-3:] if len(valid_sectors) >= 6 else valid_sectors[3:]
    
    sectors_data = []
    for sr in top_3_gainers + top_3_losers:
        status = "Tích cực" if sr.avg_change > 0 else "Tiêu cực" if sr.avg_change < 0 else "Phân hóa"
        
        symbols_str = sr.top_symbols or ""
        symbols_list = [s.strip() for s in symbols_str.split(",") if s.strip()]
        
        gainers = symbols_list if status == "Tích cực" else []
        losers = symbols_list if status == "Tiêu cực" else []
        
        sectors_data.append(SectorPerformance(
            name=sr.sector,
            avg_change=float(sr.avg_change),
            top_gainers=gainers,
            top_losers=losers,
            status=status
        ))

    # 4. Process Foreign Trading
    f_net = float(f_total_buy - f_total_sell)
    f_status = "MUA RÒNG" if f_net > 0 else "BÁN RÒNG"

    # 5. Build Final Model
    market_index = MarketIndex(
        symbol=index_row.symbol,
        point=float(index_row.point),
        change_point=float(index_row.change_point),
        change_percent=float(index_row.change_percent),
        total_volume=int(index_row.total_volume),
        total_value=float(index_row.total_value),
        breadth=MarketBreadth(
            green=index_row.breadth_green,
            red=index_row.breadth_red,
            yellow=index_row.breadth_yellow,
            ceiling=index_row.breadth_ceiling,
            floor=index_row.breadth_floor
        )
    )

    f_trading = ForeignTrading(
        status=f_status,
        net_value=abs(f_net) / 1e9,
        top_buy=[f"{r.symbol} (+{float(r.net_val) / 1e9:,.0f} tỷ đồng)" for r in top_buy_rows],
        top_sell=[f"{r.symbol} (-{float(r.net_val) / 1e9:,.0f} tỷ đồng)" for r in top_sell_rows]
    )

    # Values that can be overridden by user
    liquidity_comment = "Thanh khoản ở mức trung bình"
    technical_score = 5
    technical_rating = "TÍCH CỰC"
    pe_ratio = 14.5
    expert_comment = "Thị trường phân hóa mạnh, chờ đợi tín hiệu dòng tiền."

    # Apply Overrides
    if payload.manual_override:
        ovr = payload.manual_override
        if ovr.pe_ratio is not None: pe_ratio = ovr.pe_ratio
        if ovr.technical_score is not None: 
            technical_score = ovr.technical_score
            # Auto-calculate rating based on score ranges if score is overridden
            if technical_score >= 4:
                technical_rating = "TÍCH CỰC"
            elif technical_score <= -4:
                technical_rating = "TIÊU CỰC"
            else:
                technical_rating = "TRUNG TÍNH"
                
        # If user explicitly provided a rating string, it dominates
        if ovr.technical_rating is not None: 
            technical_rating = ovr.technical_rating
            
        if ovr.expert_comment is not None: expert_comment = ovr.expert_comment
        if ovr.liquidity_comment is not None: liquidity_comment = ovr.liquidity_comment

    report_input = DailyReportInput(
        date=t_date.strftime("%d/%m/%Y"),
        index=market_index,
        liquidity_comment=liquidity_comment,
        impact_positive=impact_pos,
        impact_negative=impact_neg,
        sectors=sectors_data,
        foreign=f_trading,
        technical_score=technical_score,
        technical_rating=technical_rating,
        pe_ratio=pe_ratio,
        expert_comment=expert_comment
    )

    # 6. Generate Report
    engine = AIEngine()
    result = engine.generate_report(report_input)

    return {"report_content": result}

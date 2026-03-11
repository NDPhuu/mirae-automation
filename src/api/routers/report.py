from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.database import get_db
from src.api.schemas import ReportGenerateRequest, ReportGenerateResponse
from src.services.ai_engine import AIEngine
from src.models import (
    DailyReportInput, MarketIndex, MarketBreadth, 
    ForeignTrading, SectorPerformance
)

router = APIRouter(prefix="/api/v1/report", tags=["Report"])

@router.post("/generate", response_model=ReportGenerateResponse)
def generate_report(request: ReportGenerateRequest, db: Session = Depends(get_db)):
    """
    Kích hoạt AIEngine để tạo báo cáo.
    Nhận Manual Override từ frontend (Next.js) và kết hợp dữ liệu DB thực tế.
    """
    # 1. Fetch Index Data
    index_row = db.execute(text("SELECT * FROM index_snapshot ORDER BY trading_date DESC LIMIT 1")).fetchone()
    if not index_row:
        raise HTTPException(status_code=404, detail="No market data available in DB")
    
    t_date = index_row.trading_date

    # 2. Fetch Impact
    pos_rows = db.execute(text("SELECT symbol, change_percent FROM impact_metrics WHERE trading_date = :d ORDER BY impact_value DESC LIMIT 3"), {"d": t_date}).fetchall()
    neg_rows = db.execute(text("SELECT symbol, change_percent FROM impact_metrics WHERE trading_date = :d ORDER BY impact_value ASC LIMIT 3"), {"d": t_date}).fetchall()
    impact_pos = [f"{r.symbol} (+{r.change_percent}%)" for r in pos_rows]
    impact_neg = [f"{r.symbol} ({r.change_percent}%)" for r in neg_rows]

    # 3. Fetch Sectors
    sectors_data = []
    sector_rows = db.execute(text("SELECT sector, avg_change, total_stocks FROM sector_performance_metrics WHERE trading_date = :d"), {"d": t_date}).fetchall()
    for sr in sector_rows:
        status = "Tích cực" if sr.avg_change > 0 else "Tiêu cực" if sr.avg_change < 0 else "Phân hóa"
        # Dummy top gainers/losers for now, ideally populated by joining impact_metrics
        sectors_data.append(SectorPerformance(
            name=sr.sector,
            avg_change=float(sr.avg_change),
            top_gainers=[],
            top_losers=[],
            status=status
        ))

    # 4. Fetch Foreign Trading
    f_total_buy = db.execute(text("SELECT SUM(f_buy_val) FROM foreign_trading WHERE trading_date = :d"), {"d": t_date}).scalar() or 0.0
    f_total_sell = db.execute(text("SELECT SUM(f_sell_val) FROM foreign_trading WHERE trading_date = :d"), {"d": t_date}).scalar() or 0.0
    f_net = float(f_total_buy - f_total_sell)
    f_status = "MUA RÒNG" if f_net > 0 else "BÁN RÒNG"

    top_buy_rows = db.execute(text("SELECT symbol FROM foreign_trading WHERE trading_date = :d AND net_val > 0 ORDER BY net_val DESC LIMIT 3"), {"d": t_date}).fetchall()
    top_sell_rows = db.execute(text("SELECT symbol FROM foreign_trading WHERE trading_date = :d AND net_val < 0 ORDER BY net_val ASC LIMIT 3"), {"d": t_date}).fetchall()

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
        net_value=abs(f_net),
        top_buy=[r.symbol for r in top_buy_rows],
        top_sell=[r.symbol for r in top_sell_rows]
    )

    # Values that can be overridden by user
    liquidity_comment = "Thanh khoản ở mức trung bình"
    technical_score = 5
    technical_rating = "Trung lập"
    pe_ratio = 14.5
    expert_comment = "Thị trường phân hóa mạnh, chờ đợi tín hiệu dòng tiền."

    # Apply Overrides
    if request.manual_override:
        ovr = request.manual_override
        if ovr.pe_ratio is not None: pe_ratio = ovr.pe_ratio
        if ovr.technical_score is not None: technical_score = ovr.technical_score
        if ovr.technical_rating is not None: technical_rating = ovr.technical_rating
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

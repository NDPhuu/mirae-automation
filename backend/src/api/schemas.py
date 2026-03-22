from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class IndexOverviewResponse(BaseModel):
    symbol: str
    trading_date: date
    point: Optional[float]
    change_point: Optional[float]
    change_percent: Optional[float]
    total_volume: Optional[int]
    total_value: Optional[float]
    breadth_green: Optional[int]
    breadth_red: Optional[int]
    breadth_yellow: Optional[int]
    breadth_ceiling: Optional[int]
    breadth_floor: Optional[int]

    class Config:
        from_attributes = True

class ImpactMetric(BaseModel):
    symbol: str
    sector: Optional[str]
    price: float
    ref_price: float
    change_percent: float
    impact_value: float

class TopImpactResponse(BaseModel):
    positive: List[ImpactMetric]
    negative: List[ImpactMetric]

class ForeignTradeMetric(BaseModel):
    symbol: str
    trading_date: date
    f_buy_val: float
    f_sell_val: float
    net_val: float

    class Config:
        from_attributes = True

class ForeignTradingResponse(BaseModel):
    top_buy: List[ForeignTradeMetric]
    top_sell: List[ForeignTradeMetric]
    total_net_val: float

class SectorPerformanceMetric(BaseModel):
    trading_date: date
    sector: str
    avg_change: float
    total_stocks: int
    top_symbols: Optional[str] = None

class SectorPerformanceResponse(BaseModel):
    sectors: List[SectorPerformanceMetric]

class ManualOverrideRequest(BaseModel):
    pe_ratio: Optional[float] = None
    technical_score: Optional[int] = None
    technical_rating: Optional[str] = None
    expert_comment: Optional[str] = None
    liquidity_comment: Optional[str] = None

class ReportGenerateRequest(BaseModel):
    manual_override: Optional[ManualOverrideRequest] = None

class ReportGenerateResponse(BaseModel):
    report_content: str

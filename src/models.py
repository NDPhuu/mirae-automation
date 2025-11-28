# File: src/models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

# --- 1. DỮ LIỆU CƠ BẢN ---
class MarketBreadth(BaseModel):
    green: int = 0
    red: int = 0
    yellow: int = 0
    ceiling: int = 0
    floor: int = 0

class MarketIndex(BaseModel):
    symbol: str = "VNINDEX"
    point: float
    change_point: float
    change_percent: float
    total_volume: int = 0 # Khối lượng giao dịch (Triệu đồng)
    total_value: float # Giá trị giao dịch (Tỷ đồng)
    breadth: MarketBreadth

# --- 2. DỮ LIỆU CHI TIẾT ---
class StockData(BaseModel):
    """Dùng để lưu giá của từng mã trong nhóm ngành"""
    symbol: str
    price: float
    change_percent: float

class SectorPerformance(BaseModel):
    """Kết quả phân tích ngành"""
    name: str # VD: Ngân hàng
    avg_change: float # % Tăng giảm trung bình
    top_gainers: List[str] # Các mã tăng mạnh nhất trong ngành
    top_losers: List[str] # Các mã giảm mạnh nhất
    status: str # "Tích cực", "Tiêu cực", "Phân hóa"

class ForeignTrading(BaseModel):
    status: str # MUA RÒNG / BÁN RÒNG
    net_value: float
    top_buy: List[str]
    top_sell: List[str]

# --- 3. DỮ LIỆU TỔNG HỢP (INPUT CHO AI) ---
class DailyReportInput(BaseModel):
    """Object chứa TOÀN BỘ dữ liệu để ném vào Prompt"""
    date: str
    index: MarketIndex
    liquidity_comment: str # "Cao hơn trung bình", "Thấp hơn"...
    impact_positive: List[str] # ["VCB (+2%)", "BID (+1%)"]
    impact_negative: List[str]
    sectors: List[SectorPerformance]
    foreign: ForeignTrading
    technical_score: int
    technical_rating: str
    pe_ratio: float
    expert_comment: str
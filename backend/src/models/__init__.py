# File: src/models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

# --- 1. Dá»® LIá»†U CÆ  Báº¢N ---
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
    total_volume: int = 0 # Khá»‘i lÆ°á»£ng giao dá»‹ch (Triá»‡u Ä‘á»“ng)
    total_value: float # GiÃ¡ trá»‹ giao dá»‹ch (Tá»· Ä‘á»“ng)
    breadth: MarketBreadth

# --- 2. Dá»® LIá»†U CHI TIáº¾T ---
class StockData(BaseModel):
    """LÆ°u giÃ¡ vÃ  cÃ¡c chá»‰ sá»‘ chuáº©n hÃ³a cá»§a tá»«ng mÃ£ chá»©ng khoÃ¡n"""
    symbol: str
    price: float
    ref_price: float = 0.0
    change_percent: float
    shares: int = 0
    volume: int = 0
    f_buy_val: float = 0.0
    f_sell_val: float = 0.0

class SectorPerformance(BaseModel):
    """Káº¿t quáº£ phÃ¢n tÃ­ch ngÃ nh"""
    name: str # VD: NgÃ¢n hÃ ng
    avg_change: float # % TÄƒng giáº£m trung bÃ¬nh
    top_gainers: List[str] # CÃ¡c mÃ£ tÄƒng máº¡nh nháº¥t trong ngÃ nh
    top_losers: List[str] # CÃ¡c mÃ£ giáº£m máº¡nh nháº¥t
    status: str # "TÃ­ch cá»±c", "TiÃªu cá»±c", "PhÃ¢n hÃ³a"

class ForeignTrading(BaseModel):
    status: str # MUA RÃ’NG / BÃN RÃ’NG
    net_value: float
    top_buy: List[str]
    top_sell: List[str]

# --- 3. Dá»® LIá»†U Tá»”NG Há»¢P (INPUT CHO AI) ---
class DailyReportInput(BaseModel):
    """Object chá»©a TOÃ€N Bá»˜ dá»¯ liá»‡u Ä‘á»ƒ nÃ©m vÃ o Prompt"""
    date: str
    index: MarketIndex
    liquidity_comment: str # "Cao hÆ¡n trung bÃ¬nh", "Tháº¥p hÆ¡n"...
    impact_positive: List[str] # ["VCB (+2%)", "BID (+1%)"]
    impact_negative: List[str]
    sectors: List[SectorPerformance]
    foreign: ForeignTrading
    technical_score: int
    technical_rating: str
    pe_ratio: float
    expert_comment: str

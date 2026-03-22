import logging
from typing import List, Dict, Tuple, Any
from src.models import MarketIndex, MarketBreadth, StockData
from src.cache import db

logger = logging.getLogger(__name__)

class DataAggregator:
    def __init__(self):
        # Không cần khởi tạo DNSE hay SSI nữa, mọi thứ đã có Streamer Daemon lo
        pass

    def fetch_market_data(self, stock_list: List[str]) -> Tuple[MarketIndex, Dict[str, StockData]]:
        """
        Fetches stock data instantly from the local SQLite cache via Background Streamer.
        """
        # 1. Lấy dữ liệu VNINDEX từ Cache
        index_row = db.get_market_index("VNINDEX")
        if not index_row:
            logger.warning("Không tìm thấy dữ liệu VNINDEX trong Cache. Vui lòng bật Market Streamer Daemon.")
            return None, {}

        breadth = MarketBreadth(
            green=index_row.get("breadth_green", 0),
            red=index_row.get("breadth_red", 0),
            yellow=index_row.get("breadth_yellow", 0),
            ceiling=index_row.get("breadth_ceiling", 0),
            floor=index_row.get("breadth_floor", 0)
        )
        market_index = MarketIndex(
            symbol="VNINDEX",
            point=index_row.get("point", 0.0),
            change_point=index_row.get("change_point", 0.0),
            change_percent=index_row.get("change_percent", 0.0),
            total_volume=index_row.get("total_volume", 0.0),
            total_value=index_row.get("total_value", 0.0),
            breadth=breadth
        )

        # 2. Lấy dữ liệu danh sách cổ phiếu từ Cache
        cached_stocks = db.get_stocks(stock_list)
        unified_stocks: Dict[str, StockData] = {}

        for sym, row in cached_stocks.items():
            unified_stocks[sym] = StockData(
                symbol=sym,
                price=float(row.get("price") or 0.0),
                ref_price=float(row.get("ref_price") or 0.0),
                change_percent=float(row.get("change_percent") or 0.0),
                shares=int(row.get("shares") or 0),
                volume=int(row.get("volume") or 0),
                f_buy_val=float(row.get("f_buy_val") or 0.0),
                f_sell_val=float(row.get("f_sell_val") or 0.0)
            )

        return market_index, unified_stocks

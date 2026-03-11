import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.cache import db
from src.services.market_logic import MarketLogic
from src.models import StockData, MarketIndex, MarketBreadth

def debug_system():
    print("Checking SQLite DB...")
    index_row = db.get_market_index("VNINDEX")
    if index_row:
        print(f"VNINDEX found: {index_row['point']}")
    else:
        print("VNINDEX NOT FOUND in DB.")
        
    stocks = db.get_stocks(['VIC', 'VCB', 'HPG', 'MBB', 'CTG'])
    for sym, s in stocks.items():
        print(f"Stock {sym}: Price={s['price']}, Shares={s['shares']}")
        
    # Test logic
    logic = MarketLogic()
    # Mock data to see if calculation works
    stocks_objects = {}
    for sym, s in stocks.items():
         stocks_objects[sym] = StockData(
            symbol=sym,
            price=s['price'],
            ref_price=s['ref_price'],
            change_percent=s['change_percent'],
            shares=s['shares'],
            volume=s['volume'],
            f_buy_val=s['f_buy_val'],
            f_sell_val=s['f_sell_val']
        )
    
    idx = MarketIndex(
        symbol="VNINDEX", point=1100.0, change_point=0, change_percent=0,
        total_volume=0, total_value=0, breadth=MarketBreadth(green=0, red=0, yellow=0, ceiling=0, floor=0)
    )
    
    pos, neg = logic.get_top_impact(stocks_objects, idx.point)
    print(f"Logic Result - Positive: {pos}")
    print(f"Logic Result - Negative: {neg}")

if __name__ == "__main__":
    debug_system()

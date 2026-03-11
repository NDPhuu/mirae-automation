import os
import sys

# Add root dir to sys path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(root_dir)

from src.models import StockData, MarketIndex
from src.services.market_logic import MarketLogic

def test_top_impact():
    print("--- TESTING TOP IMPACT MATH ---")
    stocks_dict = {
        "AAA": StockData(symbol="AAA", price=12000, ref_price=10000, change_percent=20.0, shares=1000, volume=0), # Cap: 12M
        "BBB": StockData(symbol="BBB", price=25000, ref_price=20000, change_percent=25.0, shares=2000, volume=0), # Cap: 50M
        "CCC": StockData(symbol="CCC", price=8000, ref_price=10000, change_percent=-20.0, shares=5000, volume=0)  # Cap: 40M
    }
    # Total Cap: 102M
    # AAA weight = 12/102 = 11.76%, Return = 20% -> impact_pct = 2.35%
    # BBB weight = 50/102 = 49.02%, Return = 25% -> impact_pct = 12.25%
    # CCC weight = 40/102 = 39.21%, Return = -20% -> impact_pct = -7.84%
    
    # VNINDEX = 1000. 
    # AAA impact point = 23.5
    # BBB impact point = 122.5
    # CCC impact point = -78.4
    
    # Expected ranking Positive: BBB, AAA
    # Expected ranking Negative: CCC
    
    logic = MarketLogic()
    pos, neg = logic.get_top_impact(stocks_dict, 1000)
    
    print("Positive:", pos)
    print("Negative:", neg)
    
    assert pos == ['BBB (+25.00%)', 'AAA (+20.00%)'], f"Expected ['BBB (+25.00%)', 'AAA (+20.00%)'], got {pos}"
    assert neg == ['CCC (-20.00%)'], f"Expected ['CCC (-20.00%)'], got {neg}"
    print("✅ Top Impact test passed!")

if __name__ == "__main__":
    test_top_impact()

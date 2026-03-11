import sys
import os
from pprint import pprint
# Đảm bảo có thể import src module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sys
import os
from pprint import pprint
# Đảm bảo có thể import src module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.market_data_aggregator import MarketDataAggregator

def test_unified_aggregator():
    print("--- Testing Unified MarketDataAggregator ---")
    aggregator = MarketDataAggregator()
    
    symbols = ["HPG", "SSI", "VND"]
    print(f"Fetching unified market data for {symbols}...")
    
    index_data, unified_stocks = aggregator.fetch_unified_market_data(symbols)
    
    print("\n--- VNINDEX Data ---")
    if index_data:
        # Tương thích Pydantic v1 & v2
        if hasattr(index_data, "model_dump"):
            pprint(index_data.model_dump())
        elif hasattr(index_data, "dict"):
            pprint(index_data.dict())
        else:
            pprint(index_data)
    else:
        print("No index data received.")
        
    print("\n--- Unified Stocks Data ---")
    if unified_stocks:
        pprint(unified_stocks)
    else:
        print("No stock data received.")

if __name__ == "__main__":
    test_unified_aggregator()
